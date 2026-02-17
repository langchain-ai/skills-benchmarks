"""LangSmith language-specific skills benchmark fixtures.

This benchmark tests whether language-specific skill names help Claude
add LangSmith tracing correctly to both Python and TypeScript agents.
"""

import os
import uuid
from pathlib import Path

import pytest

ENVIRONMENT_DIR = Path(__file__).parent / "environment"


def _get_langsmith_client():
    """Get LangSmith client."""
    try:
        from langsmith import Client

        return Client(), None
    except Exception as e:
        return None, str(e)


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


@pytest.fixture
def environment_dir():
    """Path to environment directory with backend and frontend agents."""
    return ENVIRONMENT_DIR


def _create_dataset(client, name: str, description: str, examples: list[dict]) -> str:
    """Create a dataset with examples and return its name."""
    dataset = client.create_dataset(dataset_name=name, description=description)
    for example in examples:
        client.create_example(
            inputs=example["inputs"],
            outputs=example["outputs"],
            dataset_id=dataset.id,
        )
    return name


@pytest.fixture
def langsmith_dataset(langsmith_project):
    """Create two datasets in LangSmith - one for each agent (Python/TypeScript).

    Backend (Python): SQL agent with trajectory dataset (tool call sequences)
    Frontend (TypeScript): Support bot with final_response dataset (query/response)
    """
    client, error = _get_langsmith_client()
    if not client:
        pytest.skip(f"LangSmith client not available: {error}")

    suffix = uuid.uuid4().hex[:8]

    # Python backend: SQL agent trajectory dataset (tool call sequences)
    py_dataset = _create_dataset(
        client,
        f"benchmark-sql-{suffix}",
        "Trajectory dataset for Python SQL agent - tracks tool call sequences",
        [
            {
                "inputs": {
                    "messages": [{"content": "Which albums have the most tracks?", "type": "human"}]
                },
                "outputs": {"expected_trajectory": ["get_database_schema", "execute_sql_query"]},
            },
            {
                "inputs": {
                    "messages": [
                        {"content": "Which 3 genres generated the most revenue?", "type": "human"}
                    ]
                },
                "outputs": {"expected_trajectory": ["get_database_schema", "execute_sql_query"]},
            },
            {
                "inputs": {
                    "messages": [
                        {
                            "content": "What are the most popular artists by number of tracks?",
                            "type": "human",
                        }
                    ]
                },
                "outputs": {"expected_trajectory": ["get_database_schema", "execute_sql_query"]},
            },
        ],
    )

    # TypeScript frontend: Support bot final_response dataset (query/response pairs)
    ts_dataset = _create_dataset(
        client,
        f"benchmark-support-{suffix}",
        "Final response dataset for TypeScript support bot - compares response outputs",
        [
            {
                "inputs": {"query": "Does the blue widget come in large?"},
                "outputs": {
                    "response": "Yes, the blue widget is available in small, medium, and large sizes."
                },
            },
            {
                "inputs": {"query": "How do I contact support?"},
                "outputs": {
                    "response": "You can reach our support team at support@example.com or call 1-800-SUPPORT."
                },
            },
        ],
    )

    print(f"\n{'=' * 60}")
    print("LANGSMITH DATASETS:")
    print(f"  Backend (trajectory): {py_dataset}")
    print(f"  Frontend (final_response): {ts_dataset}")
    print(f"{'=' * 60}\n")

    yield {"py": py_dataset, "ts": ts_dataset}

    # Cleanup
    for dataset_name in [py_dataset, ts_dataset]:
        try:
            client.delete_dataset(dataset_name=dataset_name)
            print(f"Deleted dataset: {dataset_name}")
        except Exception as e:
            print(f"Warning: Could not delete dataset {dataset_name}: {e}")
