"""Ground truth generators for LangSmith Synergy experiment.

Generates expected outputs AFTER Claude runs, creating "correct answers"
that validators compare against.

Generated files:
- expected_traces.json      - Trace data with tool calls (using run_type="tool")
- expected_dataset.json     - Dataset structure based on real skill script output
- evaluator_test_cases.json - Test cases for evaluator validation

Called by the runner in Phase 3 (GROUND TRUTH).
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scaffold.utils import retry_with_backoff


def _get_langsmith_client():
    """Get LangSmith client."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    from langsmith import Client
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return None, "LANGSMITH_API_KEY not set"
    return Client(api_key=api_key), None


def generate_expected_traces(
    test_dir: Path,
    project: str = None,
    limit: int = 5,
    max_age_minutes: int = 1440,
) -> List[Dict]:
    """Generate expected traces using skill script patterns.

    Uses run_type="tool" filter to get tool calls - the key skill script pattern.
    This captures data that can ONLY be obtained by using the correct approach.

    Args:
        test_dir: Test directory to save expected_traces.json
        project: LangSmith project name (defaults to LANGSMITH_PROJECT env var)
        limit: Max number of traces to fetch (sql_agent.py generates exactly 5 distinct queries)
        max_age_minutes: Only look at traces from the last N minutes (default: 24 hours)
    """
    project = project or os.environ.get("LANGSMITH_PROJECT")
    if not project:
        return []

    client, error = _get_langsmith_client()
    if error:
        print(f"Warning: {error}")
        return []

    try:
        from datetime import timezone
        start_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)

        # Fetch the most recent traces (sql_agent.py generates exactly 5 distinct queries)
        traces = retry_with_backoff(lambda: list(client.list_runs(
            project_name=project, is_root=True, start_time=start_time, limit=limit
        )))

        expected = []
        for trace in traces:
            trace_id = str(getattr(trace, "trace_id", trace.id))

            # Get tool calls using run_type="tool" (key skill script pattern)
            try:
                tools = retry_with_backoff(lambda t=trace_id: list(client.list_runs(
                    project_name=project,
                    trace_id=t,
                    run_type="tool",
                    limit=30,
                )))

                # Extract tool sequence (ordered by start_time)
                tool_sequence = [
                    t.name for t in sorted(tools, key=lambda x: x.start_time or datetime.min)
                ]
            except Exception:
                tool_sequence = []

            # Extract inputs from trace
            inputs = {}
            if trace.inputs:
                inputs = dict(trace.inputs)
                # Normalize common input patterns
                if "input" in inputs and "query" not in inputs:
                    inputs["query"] = inputs.get("input")

            expected.append({
                "trace_id": trace_id,
                "name": trace.name,
                "run_type": trace.run_type,
                "inputs": inputs,
                "tool_sequence": tool_sequence,
                "tool_count": len(tool_sequence),
            })

        # Save to file
        output_path = test_dir / "expected_traces.json"
        output_path.write_text(json.dumps(expected, indent=2, default=str))

        return expected

    except Exception as e:
        print(f"Warning: generate_expected_traces failed: {e}")
        return []


def generate_expected_dataset(test_dir: Path, traces: List[Dict] = None) -> Dict:
    """Generate expected dataset structure.

    Uses the same format as skill script output:
    {
        "trace_id": "...",
        "inputs": {"query": "..."},
        "outputs": {"expected_trajectory": ["tool1", "tool2", ...]}
    }
    """
    if traces is None:
        traces_path = test_dir / "expected_traces.json"
        if traces_path.exists():
            traces = json.loads(traces_path.read_text())
        else:
            traces = []

    if not traces:
        return {"examples": [], "error": "No traces available"}

    examples = []
    for trace in traces:
        tool_sequence = trace.get("tool_sequence", [])
        if not tool_sequence:
            continue

        example = {
            "trace_id": trace.get("trace_id"),
            "inputs": trace.get("inputs", {}),
            "outputs": {
                "expected_trajectory": tool_sequence
            }
        }
        examples.append(example)

    dataset = {
        "name": "expected_trajectory_dataset",
        "description": "Expected trajectory dataset from LangSmith traces",
        "examples": examples,
    }

    output_path = test_dir / "expected_dataset.json"
    output_path.write_text(json.dumps(dataset, indent=2))

    return dataset


def generate_evaluator_test_cases(test_dir: Path, traces: List[Dict] = None) -> List[Dict]:
    """Generate test cases for evaluator validation.

    Creates test cases with known expected results that we run Claude's
    evaluator through. Tests:
    - Perfect match (same trajectory) -> should score high
    - Partial match (some tools) -> should score medium
    - No match (different tools) -> should score low
    - Empty trajectory -> should not crash
    """
    if traces is None:
        traces_path = test_dir / "expected_traces.json"
        if traces_path.exists():
            traces = json.loads(traces_path.read_text())
        else:
            traces = []

    # Get base tools from first trace with tools, or use defaults
    base_tools = ["execute_sql", "get_database_info"]
    for trace in traces:
        tools = trace.get("tool_sequence", [])
        if tools:
            base_tools = tools[:5]  # Take first 5 tools
            break

    test_cases = []

    # Test Case 1: Perfect match - same trajectory should score HIGH (>= 0.8)
    test_cases.append({
        "name": "perfect_match",
        "description": "Identical trajectory should score high",
        "run": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": base_tools}
        },
        "example": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": base_tools}
        },
        "expected_result": {
            "should_pass": True,
            "min_score": 1.0,
            "reason": "Identical trajectories should score 1.0"
        }
    })

    # Test Case 2: Partial match - some tools match should score MEDIUM (0.3-0.8)
    partial_tools = base_tools[:max(1, len(base_tools)//2)]
    test_cases.append({
        "name": "partial_match",
        "description": "Partial tool overlap should score medium",
        "run": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": partial_tools}
        },
        "example": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": base_tools}
        },
        "expected_result": {
            "should_pass": True,
            "min_score": 0.2,
            "max_score": 0.9,
            "reason": "Partial overlap should score between 0.2 and 0.9"
        }
    })

    # Test Case 3: No match - different tools should score LOW (<= 0.3)
    test_cases.append({
        "name": "no_match",
        "description": "Completely different trajectory should score low",
        "run": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": ["unknown_tool_xyz"]}
        },
        "example": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": base_tools}
        },
        "expected_result": {
            "should_pass": True,
            "max_score": 0.4,
            "reason": "No tool overlap should score <= 0.4"
        }
    })

    # Test Case 4: Empty trajectory - should handle gracefully
    test_cases.append({
        "name": "empty_trajectory",
        "description": "Empty trajectory should not crash",
        "run": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": []}
        },
        "example": {
            "inputs": {"query": "Test query"},
            "outputs": {"expected_trajectory": base_tools}
        },
        "expected_result": {
            "should_not_crash": True,
            "reason": "Should handle empty trajectory without crashing"
        }
    })

    output_path = test_dir / "evaluator_test_cases.json"
    output_path.write_text(json.dumps(test_cases, indent=2))

    return test_cases


def generate_all_ground_truth(test_dir: Path) -> Dict[str, Any]:
    """Generate all ground truth files for the test.

    Main entry point called by the runner in Phase 3.
    """
    result = {}

    # Generate traces first (other generators depend on this)
    traces = generate_expected_traces(test_dir)
    result["traces"] = traces
    result["trace_count"] = len(traces)

    # Generate expected dataset from traces
    dataset = generate_expected_dataset(test_dir, traces)
    result["dataset"] = dataset
    result["dataset_example_count"] = len(dataset.get("examples", []))

    # Generate evaluator test cases
    test_cases = generate_evaluator_test_cases(test_dir, traces)
    result["evaluator_test_cases"] = test_cases
    result["test_case_count"] = len(test_cases)

    return result
