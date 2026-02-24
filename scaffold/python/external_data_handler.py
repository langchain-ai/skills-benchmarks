"""External data handlers for test setup and cleanup.

Handlers manage external LangSmith resources during tests.
All resources use a namespace pattern: bench-{type}-{run_id}

Available handlers:
    - upload_traces: Upload trace fixtures to a LangSmith project
    - cleanup_namespace: Delete all LangSmith resources ending with -{run_id}
"""

import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


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


def upload_traces(project: str, data_dir: Path, **kwargs) -> dict[str, str]:
    """Upload trace fixtures from jsonl files to LangSmith project.

    Required for tasks like ls-multiskill-* that need pre-existing traces.

    Args:
        project: LangSmith project name to upload to
        data_dir: Directory containing trace_*.jsonl files
        **kwargs: Additional arguments (ignored)

    Returns:
        Mapping of original trace_id -> new trace_id
    """
    client, error = _get_langsmith_client()
    if error:
        print(f"Could not upload traces: {error}")
        return {}

    # Ensure data_dir is a Path
    data_dir = Path(data_dir) if not isinstance(data_dir, Path) else data_dir

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


def upload_datasets(data_dir: Path, run_id: str, **kwargs) -> dict[str, str]:
    """Upload dataset JSON files to LangSmith using naming convention.

    File naming convention: {type}_*_dataset.json → bench-{type}-{run_id}
    Example: sql_agent_trajectory_dataset.json → bench-sql-{run_id}

    Args:
        data_dir: Directory containing *_dataset.json files
        run_id: Unique identifier for namespacing
        **kwargs: Additional arguments (ignored)

    Returns:
        Mapping of file names to created dataset names
    """
    client, error = _get_langsmith_client()
    if error:
        print(f"Could not upload datasets: {error}")
        return {}

    data_dir = Path(data_dir) if not isinstance(data_dir, Path) else data_dir
    created = {}

    for file_path in sorted(data_dir.glob("*_dataset.json")):
        # Extract type from filename: sql_agent_trajectory_dataset.json → sql
        file_type = file_path.name.split("_")[0]
        dataset_name = f"bench-{file_type}-{run_id}"

        try:
            examples = json.loads(file_path.read_text())
            if not isinstance(examples, list):
                examples = [examples]

            # Create dataset and add examples
            dataset = client.create_dataset(dataset_name=dataset_name)
            inputs = [ex.get("inputs", {}) for ex in examples]
            outputs = [ex.get("outputs", {}) for ex in examples]
            client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

            created[file_path.name] = dataset_name
            print(f"  Uploaded {len(examples)} examples to {dataset_name}")
        except Exception as e:
            print(f"  Failed to upload {file_path.name}: {e}")

    return created


def _delete_evaluators_for_datasets(dataset_ids: set[str]) -> list[str]:
    """Delete all evaluators attached to the given dataset IDs.

    Args:
        dataset_ids: Set of dataset IDs to find evaluators for

    Returns:
        List of deleted evaluator names
    """
    if not dataset_ids:
        return []

    api_key = os.environ.get("LANGSMITH_API_KEY")
    api_url = os.environ.get("LANGSMITH_API_URL", "https://api.smith.langchain.com")

    if not api_key:
        return []

    headers = {"x-api-key": api_key}
    deleted = []

    try:
        response = requests.get(f"{api_url}/runs/rules", headers=headers)
        if not response.ok:
            return []

        for rule in response.json():
            rule_dataset_id = rule.get("dataset_id")
            if rule_dataset_id and rule_dataset_id in dataset_ids:
                rule_id = rule.get("id")
                rule_name = rule.get("display_name", "unnamed")
                try:
                    del_resp = requests.delete(
                        f"{api_url}/runs/rules/{rule_id}", headers=headers
                    )
                    if del_resp.ok:
                        deleted.append(rule_name)
                        print(f"  Deleted evaluator: {rule_name}")
                except Exception as e:
                    print(f"  Failed to delete evaluator {rule_name}: {e}")
    except Exception as e:
        print(f"  Error cleaning up evaluators: {e}")

    return deleted


def cleanup_namespace(run_id: str, **kwargs) -> dict[str, list[str]]:
    """Delete all LangSmith resources matching the run_id namespace.

    Finds and deletes:
    - Projects ending with -{run_id}
    - Evaluators attached to datasets ending with -{run_id}
    - Datasets ending with -{run_id}

    Args:
        run_id: Unique identifier to match in resource names

    Returns:
        Dict with lists of deleted resource names by type
    """
    client, error = _get_langsmith_client()
    if error:
        print(f"Could not cleanup namespace: {error}")
        return {}

    deleted = {"projects": [], "evaluators": [], "datasets": []}
    suffix = f"-{run_id}"

    # Delete matching projects
    try:
        for project in client.list_projects():
            if project.name.endswith(suffix):
                try:
                    client.delete_project(project_name=project.name)
                    deleted["projects"].append(project.name)
                    print(f"  Deleted project: {project.name}")
                except Exception as e:
                    print(f"  Failed to delete project {project.name}: {e}")
    except Exception as e:
        print(f"  Error listing projects: {e}")

    # Find matching datasets and their IDs (needed for evaluator cleanup)
    datasets_to_delete = []
    try:
        for dataset in client.list_datasets():
            if dataset.name.endswith(suffix):
                datasets_to_delete.append((dataset.name, str(dataset.id)))
    except Exception as e:
        print(f"  Error listing datasets: {e}")

    # Delete evaluators attached to matching datasets BEFORE deleting datasets
    if datasets_to_delete:
        dataset_ids = {ds_id for _, ds_id in datasets_to_delete}
        deleted["evaluators"] = _delete_evaluators_for_datasets(dataset_ids)

    # Delete matching datasets
    for dataset_name, _ in datasets_to_delete:
        try:
            client.delete_dataset(dataset_name=dataset_name)
            deleted["datasets"].append(dataset_name)
            print(f"  Deleted dataset: {dataset_name}")
        except Exception as e:
            print(f"  Failed to delete dataset {dataset_name}: {e}")

    return deleted


# Registry of available handlers
HANDLERS = {
    "upload_traces": upload_traces,
    "upload_datasets": upload_datasets,
    "cleanup_namespace": cleanup_namespace,
}


def run_handler(handler_name: str, **kwargs) -> Any:
    """Run a named handler."""
    if handler_name not in HANDLERS:
        raise ValueError(f"Unknown handler: {handler_name}. Available: {list(HANDLERS.keys())}")
    return HANDLERS[handler_name](**kwargs)


def run_task_handlers(
    data_handlers: list, data_dir: Path, project: str | None, run_id: str | None = None
) -> dict[str, str]:
    """Run all data handlers for a task.

    Args:
        data_handlers: List of DataHandler objects from task config
        data_dir: Task's data directory
        project: LangSmith project name
        run_id: Unique identifier for namespacing

    Returns:
        trace_id_map: Mapping of old trace IDs to new ones (from upload_traces)
    """
    trace_id_map = {}
    if not data_dir.exists():
        return trace_id_map

    for handler in data_handlers:
        if list(data_dir.glob(handler.pattern)):
            print(f"\nRunning {handler.handler}...")
            # Build handler kwargs from handler config
            kwargs = {"project": project, "data_dir": data_dir, "run_id": run_id}
            if hasattr(handler, "args") and handler.args:
                kwargs.update(handler.args)
            result = run_handler(handler.handler, **kwargs)
            if handler.handler == "upload_traces" and result:
                trace_id_map = result

    return trace_id_map
