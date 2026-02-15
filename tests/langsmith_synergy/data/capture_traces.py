#!/usr/bin/env python3
"""Capture full trace structure from LangSmith for fixture generation.

Usage:
    # Capture traces from current LANGSMITH_PROJECT
    python capture_traces.py

    # Capture from specific project
    LANGSMITH_PROJECT=my-project python capture_traces.py

    # Capture specific trace IDs
    python capture_traces.py --trace-ids id1,id2,id3

This creates/updates traces.json with full trace structure that can be
exactly replayed to any LangSmith project.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scaffold import retry_with_backoff


def get_langsmith_client():
    """Get LangSmith client."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    from langsmith import Client
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        print("Error: LANGSMITH_API_KEY not set")
        sys.exit(1)
    return Client(api_key=api_key)


def capture_trace(client, project: str, trace_id: str) -> dict:
    """Capture complete trace structure."""
    runs = retry_with_backoff(lambda: list(client.list_runs(
        project_name=project,
        trace_id=trace_id,
        limit=100,
    )))

    run_data = []
    for run in runs:
        run_data.append({
            "id": str(run.id),
            "parent_run_id": str(run.parent_run_id) if run.parent_run_id else None,
            "name": run.name,
            "run_type": run.run_type,
            "inputs": dict(run.inputs) if run.inputs else {},
            "outputs": dict(run.outputs) if run.outputs else {},
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
        })

    # Find root run to get query
    root = next((r for r in run_data if r["parent_run_id"] is None), None)
    query = ""
    if root and root.get("inputs"):
        messages = root["inputs"].get("messages", [])
        if messages and isinstance(messages, list):
            first_msg = messages[0]
            if isinstance(first_msg, dict):
                # Standard format: {"content": "...", "type": "human"}
                query = first_msg.get("content", "")
            elif isinstance(first_msg, list) and len(first_msg) >= 2:
                # LangGraph format: ["role", "content"]
                query = first_msg[1] if first_msg[0] in ("user", "human") else ""

    # Get tool sequence
    tool_runs = [r for r in runs if r.run_type == "tool"]
    tool_runs.sort(key=lambda x: x.start_time or datetime.min)
    tool_sequence = [t.name for t in tool_runs]

    return {
        "trace_id": trace_id,
        "query": query,
        "tool_sequence": tool_sequence,
        "tool_count": len(tool_sequence),
        "runs": run_data,
    }


def capture_recent_traces(client, project: str, limit: int = 5) -> list:
    """Capture recent root traces from project."""
    start_time = datetime.now(timezone.utc) - timedelta(hours=24)

    root_runs = retry_with_backoff(lambda: list(client.list_runs(
        project_name=project,
        is_root=True,
        start_time=start_time,
        limit=limit,
    )))

    traces = []
    for run in root_runs:
        trace_id = str(getattr(run, "trace_id", run.id))
        print(f"Capturing trace {trace_id}...")
        trace_data = capture_trace(client, project, trace_id)
        traces.append(trace_data)

    return traces


def main():
    parser = argparse.ArgumentParser(description="Capture LangSmith traces for fixtures")
    parser.add_argument("--trace-ids", help="Comma-separated trace IDs to capture")
    parser.add_argument("--limit", type=int, default=5, help="Number of recent traces to capture")
    parser.add_argument("--output", default=str(Path(__file__).parent / "traces.json"))
    args = parser.parse_args()

    project = os.environ.get("LANGSMITH_PROJECT")
    if not project:
        print("Error: LANGSMITH_PROJECT env var not set")
        sys.exit(1)

    print(f"Capturing traces from project: {project}")
    client = get_langsmith_client()

    if args.trace_ids:
        trace_ids = [t.strip() for t in args.trace_ids.split(",")]
        traces = [capture_trace(client, project, tid) for tid in trace_ids]
    else:
        traces = capture_recent_traces(client, project, args.limit)

    # Build output structure
    output = {
        "description": "Full trace fixtures captured from LangSmith. Used to replay exact traces for testing.",
        "source_project": project,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "full_traces": traces,
        # Also include simplified format for backwards compatibility
        "traces": [
            {
                "trace_id": t["trace_id"],
                "name": "LangGraph",
                "run_type": "chain",
                "query": t["query"],
                "tool_sequence": t["tool_sequence"],
                "tool_count": t["tool_count"],
            }
            for t in traces
        ],
        "dataset_examples": [
            {
                "trace_id": t["trace_id"],
                "inputs": {"query": t["query"]},
                "outputs": {"expected_trajectory": t["tool_sequence"]},
            }
            for t in traces
        ],
        "evaluator_test_cases": _generate_test_cases(traces),
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved {len(traces)} traces to {output_path}")
    print(f"Total runs captured: {sum(len(t['runs']) for t in traces)}")


def _generate_test_cases(traces: list) -> list:
    """Generate evaluator test cases from captured traces."""
    # Get base tools from first trace with tools
    base_tools = ["execute_sql_query", "get_database_schema"]
    for t in traces:
        if t.get("tool_sequence"):
            base_tools = t["tool_sequence"][:5]
            break

    return [
        {
            "name": "perfect_match",
            "description": "Identical trajectory should score high",
            "run": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools}},
            "example": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools}},
            "expected_result": {"should_pass": True, "min_score": 1.0},
        },
        {
            "name": "partial_match",
            "description": "Partial overlap should score medium",
            "run": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools[:1]}},
            "example": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools}},
            "expected_result": {"should_pass": True, "min_score": 0.2, "max_score": 0.9},
        },
        {
            "name": "no_match",
            "description": "Different trajectory should score low",
            "run": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": ["unknown_tool"]}},
            "example": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools}},
            "expected_result": {"should_pass": True, "max_score": 0.4},
        },
        {
            "name": "empty_trajectory",
            "description": "Empty trajectory should not crash",
            "run": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": []}},
            "example": {"inputs": {"query": "Test"}, "outputs": {"expected_trajectory": base_tools}},
            "expected_result": {"should_not_crash": True},
        },
    ]


if __name__ == "__main__":
    main()
