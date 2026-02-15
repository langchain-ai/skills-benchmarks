"""LangSmith Synergy test fixtures.

Per-worker project isolation for parallel test execution.
Each pytest-xdist worker gets its own LangSmith project.

Fixture files (in data/):
- trace_*.jsonl             - Trace operations to replay into LangSmith
- expected_dataset.json     - Ground truth for trajectory validation
- evaluator_test_cases.json - Test cases for evaluator validation
"""

import json
import os
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from tests.benchmark_langsmith.config import ENVIRONMENT_DIR

DATA_DIR = Path(__file__).parent / "data"


def _get_langsmith_client():
    """Get LangSmith client."""
    try:
        from langsmith import Client

        return Client(), None
    except Exception as e:
        return None, str(e)


def _upload_fixture_traces(project: str) -> dict[str, str]:
    """Upload fixture traces to LangSmith project (date-shifted to now).

    Returns: Dict mapping original trace_id -> new trace_id
    """
    from langsmith import Client

    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return {}

    client = Client(api_key=api_key)
    id_mapping = {}  # old_trace_id -> new_trace_id

    for jsonl_file in sorted(DATA_DIR.glob("trace_*.jsonl")):
        operations = [
            json.loads(line) for line in jsonl_file.read_text().splitlines() if line.strip()
        ]
        if not operations:
            continue

        # Get original root trace_id and query for logging
        first_post = next(
            (
                op
                for op in operations
                if op.get("operation") == "post" and not op.get("parent_run_id")
            ),
            None,
        )
        old_trace_id = first_post.get("id") if first_post else None
        query = (
            first_post.get("inputs", {}).get("messages", [{}])[0].get("content", "")[:40]
            if first_post
            else ""
        )

        try:
            new_trace_id = _replay_operations(client, project, operations)
            if new_trace_id and old_trace_id:
                id_mapping[old_trace_id] = new_trace_id
                print(f"  Uploaded: {query}...")
        except Exception as e:
            print(f"  Failed ({query}): {e}")

    client.flush()
    return id_mapping


def _replay_operations(client, project: str, operations: list[dict]) -> str:
    """Replay trace operations with new IDs and date-shifted timestamps."""
    id_map = {
        op["id"]: str(uuid.uuid4())
        for op in operations
        if op.get("operation") == "post" and op.get("id")
    }

    def parse_ts(s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None

    timestamps = [
        parse_ts(op.get("start_time")) for op in operations if op.get("operation") == "post"
    ]
    earliest = min((t for t in timestamps if t), default=None)
    now = datetime.now(UTC)
    if earliest and earliest.tzinfo is None:
        earliest = earliest.replace(tzinfo=UTC)
    offset = (now - earliest) if earliest else timedelta(0)

    root_id = None
    for op in operations:
        new_id = id_map.get(op.get("id"), op.get("id"))
        new_parent = id_map.get(op.get("parent_run_id")) if op.get("parent_run_id") else None

        if op.get("operation") == "post":
            start = parse_ts(op.get("start_time"))
            client.create_run(
                id=new_id,
                name=op.get("name"),
                run_type=op.get("run_type"),
                inputs=op.get("inputs", {}),
                start_time=start + offset if start else None,
                parent_run_id=new_parent,
                project_name=project,
                extra=op.get("extra", {}),
                tags=op.get("tags", []),
            )
            if not op.get("parent_run_id"):
                root_id = new_id

        elif op.get("operation") == "patch":
            end = parse_ts(op.get("end_time"))
            client.update_run(
                run_id=new_id,
                end_time=end + offset if end else None,
                outputs=op.get("outputs", {}),
                error=op.get("error"),
            )

    return root_id


@pytest.fixture(scope="session")
def langsmith_project(worker_id, verify_environment):
    """Create isolated LangSmith project for this worker."""
    suffix = "main" if worker_id == "master" else worker_id
    project_name = f"benchmark-{suffix}-{uuid.uuid4().hex[:8]}"

    old_project = os.environ.get("LANGSMITH_PROJECT")
    os.environ["LANGSMITH_PROJECT"] = project_name

    print(f"\n{'=' * 60}")
    print(f"LANGSMITH PROJECT: {project_name}")
    print(f"{'=' * 60}\n")

    yield project_name

    # Cleanup
    client, _ = _get_langsmith_client()
    if client:
        try:
            client.delete_project(project_name=project_name)
            print(f"Deleted project: {project_name}")
        except Exception as e:
            print(f"Warning: Could not delete project {project_name}: {e}")

    if old_project:
        os.environ["LANGSMITH_PROJECT"] = old_project
    else:
        os.environ.pop("LANGSMITH_PROJECT", None)


@pytest.fixture(scope="session")
def langsmith_traces(langsmith_project, verify_environment):
    """Upload fixture traces to worker's LangSmith project (date-shifted to now).

    Returns: Dict with 'project' and 'trace_id_map' (old_id -> new_id mapping)
    """
    print(f"\n{'=' * 60}")
    print(f"UPLOADING FIXTURE TRACES to {langsmith_project}")
    print(f"{'=' * 60}")

    trace_id_map = _upload_fixture_traces(langsmith_project)
    if not trace_id_map:
        pytest.fail(
            "Failed to upload fixture traces - check trace_*.jsonl files exist and LANGSMITH_API_KEY is valid"
        )

    print(f"SUCCESS: Uploaded {len(trace_id_map)} traces")
    print(f"{'=' * 60}\n")

    time.sleep(3)  # Wait for LangSmith to index
    return {"project": langsmith_project, "trace_id_map": trace_id_map}


@pytest.fixture
def environment_dir():
    """Path to environment directory with Dockerfile, requirements.txt, etc."""
    return ENVIRONMENT_DIR
