"""External data handlers for test setup.

Handlers are triggered by pattern matches in task.toml setup configuration.
Each handler prepares external data sources needed for the test.

Example task.toml:
    [setup]
    [[setup.data]]
    pattern = "trace_*.jsonl"
    handler = "upload_traces"

Available handlers:
    - upload_traces: Upload trace fixtures from jsonl files to LangSmith
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


def _get_langsmith_client():
    """Get LangSmith client."""
    try:
        from langsmith import Client

        return Client(), None
    except Exception as e:
        return None, str(e)


def _parse_ts(s: str) -> datetime | None:
    """Parse ISO timestamp string, always returning UTC-aware datetime."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        # Ensure timezone-aware (some formats may not have tz info)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


def _replay_trace_operations(client: Any, project: str, operations: list[dict]) -> str | None:
    """Replay trace operations with new IDs and date-shifted timestamps.

    Uses two-step POST/PATCH approach to avoid dotted_order requirement.
    """
    import uuid

    # Build ID mapping for all post operations
    id_map = {
        op["id"]: str(uuid.uuid4())
        for op in operations
        if op.get("operation") == "post" and op.get("id")
    }
    if not id_map:
        return None

    # Calculate time shift
    timestamps = [
        _parse_ts(op.get("start_time")) for op in operations if op.get("operation") == "post"
    ]
    timestamps = [t for t in timestamps if t]
    if not timestamps:
        return None

    offset = datetime.now(UTC) - min(timestamps) - timedelta(minutes=5)

    def shift_ts(ts_str):
        ts = _parse_ts(ts_str)
        return ts + offset if ts else None

    root_id = None
    for op in operations:
        old_id = op.get("id")
        new_id = id_map.get(old_id, old_id)
        new_parent = id_map.get(op.get("parent_run_id")) if op.get("parent_run_id") else None

        if op.get("operation") == "post":
            try:
                client.create_run(
                    id=new_id,
                    name=op.get("name"),
                    run_type=op.get("run_type", "chain"),
                    inputs=op.get("inputs", {}),
                    start_time=shift_ts(op.get("start_time")),
                    parent_run_id=new_parent,
                    project_name=project,
                    extra=op.get("extra", {}),
                    tags=op.get("tags", []),
                )
                if not op.get("parent_run_id"):
                    root_id = new_id
            except Exception as e:
                print(f"    Failed: {op.get('name')}: {e}")

        elif op.get("operation") == "patch":
            try:
                client.update_run(
                    run_id=new_id,
                    end_time=shift_ts(op.get("end_time")),
                    outputs=op.get("outputs", {}),
                    error=op.get("error"),
                )
            except Exception as e:
                print(f"    Failed patch: {op.get('name')}: {e}")

    return root_id


def upload_traces(project: str, data_dir: Path) -> dict[str, str]:
    """Upload trace fixtures from jsonl files to LangSmith project.

    Required for tasks like ls-multiskill-* that need pre-existing traces.

    Args:
        project: LangSmith project name to upload to
        data_dir: Directory containing trace_*.jsonl files

    Returns:
        Mapping of original trace_id -> new trace_id
    """
    client, error = _get_langsmith_client()
    if error:
        print(f"Could not upload traces: {error}")
        return {}

    id_mapping = {}
    for jsonl_file in sorted(data_dir.glob("trace_*.jsonl")):
        operations = [
            json.loads(line) for line in jsonl_file.read_text().splitlines() if line.strip()
        ]
        if not operations:
            continue

        # Find root trace and extract query for logging
        root = next(
            (
                op
                for op in operations
                if op.get("operation") == "post" and not op.get("parent_run_id")
            ),
            None,
        )
        old_id = root.get("id") if root else None
        query = (
            root.get("inputs", {}).get("messages", [{}])[0].get("content", "")[:40] if root else ""
        )

        try:
            new_id = _replay_trace_operations(client, project, operations)
            if new_id and old_id:
                id_mapping[old_id] = new_id
                print(f"  Uploaded: {query}...")
        except Exception as e:
            print(f"  Failed ({query}): {e}")

    client.flush()
    return id_mapping


# Registry of available handlers
HANDLERS = {
    "upload_traces": upload_traces,
}


def run_handler(handler_name: str, project: str, data_dir: Path, **kwargs) -> dict:
    """Run a named handler.

    Args:
        handler_name: Name of the handler (e.g., "upload_traces")
        project: LangSmith project name
        data_dir: Directory containing data files
        **kwargs: Additional arguments passed to the handler

    Returns:
        Handler-specific result (e.g., trace ID mapping)

    Raises:
        ValueError: If handler_name is not recognized
    """
    if handler_name not in HANDLERS:
        raise ValueError(f"Unknown handler: {handler_name}. Available: {list(HANDLERS.keys())}")

    return HANDLERS[handler_name](project, data_dir, **kwargs)
