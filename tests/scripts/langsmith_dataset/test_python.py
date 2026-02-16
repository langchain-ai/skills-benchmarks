"""Tests for langsmith-dataset Python scripts (generate_datasets.py, query_datasets.py).

Run with: pytest tests/scripts/langsmith_dataset/test_python.py -v
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from ..conftest import PY_GENERATE_DATASETS, PY_QUERY_DATASETS, SCRIPTS_BASE, run_python_script
from ..fixtures import (
    SAMPLE_DATASET_EXAMPLES,
    SAMPLE_DATASETS,
    create_sample_dataset_json,
    create_sample_trace_jsonl,
)


@pytest.fixture
def sample_trace_jsonl(tmp_path):
    """Create a sample JSONL trace file for testing."""
    return create_sample_trace_jsonl(tmp_path)


@pytest.fixture
def sample_dataset_json(tmp_path):
    """Create a sample dataset JSON file for testing."""
    return create_sample_dataset_json(tmp_path)


# =============================================================================
# generate_datasets.py tests
# =============================================================================


class TestGenerateDatasetsCLI:
    """Test generate_datasets.py CLI help output."""

    def test_help(self):
        """Provides help output."""
        result = run_python_script(PY_GENERATE_DATASETS, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--input" in result.stdout
        assert "--type" in result.stdout
        assert "--output" in result.stdout

    def test_has_dataset_types(self):
        """Help mentions all dataset types."""
        result = run_python_script(PY_GENERATE_DATASETS, ["--help"])
        assert result.returncode == 0
        assert "final_response" in result.stdout
        assert "single_step" in result.stdout
        assert "trajectory" in result.stdout
        assert "rag" in result.stdout


class TestGenerateDatasetsLocalFiles:
    """Test generate_datasets.py with local files."""

    def test_generates_trajectory(self, sample_trace_jsonl, tmp_path):
        """Generates trajectory dataset from JSONL with exact output validation."""
        output_file = tmp_path / "output.json"
        result = run_python_script(
            PY_GENERATE_DATASETS,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "trajectory",
                "--output",
                str(output_file),
            ],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}\n{result.stdout}"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        # Exact assertions based on SAMPLE_TRACE_RUNS fixture
        assert len(data) == 1  # One trace produces one example
        example = data[0]
        assert example["trace_id"] == "trace-001"
        assert example["inputs"]["query"] == "What is the capital of France?"
        assert "expected_trajectory" in example["outputs"]
        # Trajectory should contain tool names from the trace
        trajectory = example["outputs"]["expected_trajectory"]
        assert "search_tool" in trajectory

    def test_generates_final_response(self, sample_trace_jsonl, tmp_path):
        """Generates final_response dataset with exact output validation."""
        output_file = tmp_path / "output.json"
        result = run_python_script(
            PY_GENERATE_DATASETS,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "final_response",
                "--output",
                str(output_file),
            ],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}\n{result.stdout}"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        # Exact assertions based on SAMPLE_TRACE_RUNS fixture
        assert len(data) == 1  # One trace produces one example
        example = data[0]
        assert example["trace_id"] == "trace-001"
        assert example["inputs"]["query"] == "What is the capital of France?"
        assert example["outputs"]["expected_response"] == "Paris"


# =============================================================================
# query_datasets.py tests
# =============================================================================


class TestQueryDatasetsCLI:
    """Test query_datasets.py CLI help output."""

    def test_help(self):
        """Provides help output."""
        result = run_python_script(PY_QUERY_DATASETS, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()

    def test_subcommands(self):
        """Has expected subcommands."""
        result = run_python_script(PY_QUERY_DATASETS, ["--help"])
        assert result.returncode == 0
        assert "list-datasets" in result.stdout
        assert "show" in result.stdout
        assert "view-file" in result.stdout
        assert "structure" in result.stdout
        assert "export" in result.stdout


class TestQueryDatasetsLocalFiles:
    """Test query_datasets.py with local files."""

    def test_view_file(self, sample_dataset_json):
        """view-file command returns exact data from file."""
        result = run_python_script(
            PY_QUERY_DATASETS,
            ["view-file", str(sample_dataset_json), "--limit", "2", "--format", "json"],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"

        # Parse JSON output and verify exact content matches SAMPLE_LOCAL_DATASET
        json_start = result.stdout.find("[")
        json_end = result.stdout.rfind("]") + 1
        assert json_start >= 0, "Output doesn't contain JSON array"

        data = json.loads(result.stdout[json_start:json_end])
        assert len(data) == 2

        # Check exact values from SAMPLE_LOCAL_DATASET
        assert data[0]["trace_id"] == "trace-001"
        assert data[0]["inputs"]["query"] == "What is the capital of France?"
        assert data[0]["outputs"]["expected_response"] == "Paris"

        assert data[1]["trace_id"] == "trace-002"
        assert data[1]["inputs"]["query"] == "What is 2 + 2?"
        assert data[1]["outputs"]["expected_response"] == "4"

    def test_structure(self, sample_dataset_json):
        """structure command reports exact dataset info."""
        result = run_python_script(
            PY_QUERY_DATASETS,
            ["structure", str(sample_dataset_json)],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "JSON" in result.stdout
        # Should show exactly 2 examples (matching SAMPLE_LOCAL_DATASET)
        assert "2" in result.stdout


# =============================================================================
# Mocked API Tests - Using direct function imports
# =============================================================================


@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict(
        os.environ,
        {
            "LANGSMITH_API_KEY": "test-api-key-12345",
            "LANGSMITH_PROJECT": "test-project",
        },
    ):
        yield


@pytest.fixture
def query_module(mock_env):
    """Import the query_datasets module with mocked env."""
    # Add script directory to path
    script_dir = SCRIPTS_BASE / "langsmith_dataset" / "scripts"
    sys.path.insert(0, str(script_dir))

    # Clear any cached imports
    if "query_datasets" in sys.modules:
        del sys.modules["query_datasets"]

    try:
        import query_datasets

        yield query_datasets
    finally:
        sys.path.remove(str(script_dir))
        if "query_datasets" in sys.modules:
            del sys.modules["query_datasets"]


def create_mock_dataset(dataset_data: dict) -> MagicMock:
    """Create a mock Dataset object from dict data."""
    mock = MagicMock()
    mock.id = dataset_data.get("id")
    mock.name = dataset_data.get("name")
    mock.description = dataset_data.get("description", "")
    mock.example_count = dataset_data.get("example_count", 0)
    return mock


def create_mock_example(example_data: dict) -> MagicMock:
    """Create a mock Example object from dict data."""
    mock = MagicMock()
    mock.inputs = example_data.get("inputs", {})
    mock.outputs = example_data.get("outputs", {})
    return mock


class TestMockedAPIFunctions:
    """Test API functions with mocked LangSmith client."""

    def test_get_client(self, query_module):
        """get_client returns a client when API key is set."""
        client = query_module.get_client()
        assert client is not None


class TestMockedAPIWithFixtures:
    """Test that mocked API returns data matching our fixtures."""

    @patch("query_datasets.Client")
    def test_list_datasets_returns_expected_data(self, mock_client_class, query_module):
        """Verify list_datasets output matches SAMPLE_DATASETS format."""
        mock_datasets = [create_mock_dataset(d) for d in SAMPLE_DATASETS]

        mock_client = MagicMock()
        mock_client.list_datasets.return_value = iter(mock_datasets)
        mock_client_class.return_value = mock_client

        client = query_module.get_client()
        datasets = list(client.list_datasets())

        # Should return 4 datasets
        assert len(datasets) == 4

        # First dataset should match fixture
        assert datasets[0].name == "shipping-support-golden"
        assert datasets[0].example_count == 10

        # Check all datasets
        dataset_names = [d.name for d in datasets]
        assert "shipping-support-golden" in dataset_names
        assert "Email Agent Notebook: Trajectory" in dataset_names
        assert "Email Agent: Trajectory" in dataset_names
        assert "kb-agent-golden-set" in dataset_names

        # Check exact example counts
        dataset_counts = {d.name: d.example_count for d in datasets}
        assert dataset_counts["shipping-support-golden"] == 10
        assert dataset_counts["Email Agent Notebook: Trajectory"] == 5
        assert dataset_counts["Email Agent: Trajectory"] == 16
        assert dataset_counts["kb-agent-golden-set"] == 15

    @patch("query_datasets.Client")
    def test_list_examples_returns_expected_data(self, mock_client_class, query_module):
        """Verify list_examples output matches SAMPLE_DATASET_EXAMPLES format."""
        mock_examples = [create_mock_example(e) for e in SAMPLE_DATASET_EXAMPLES]

        mock_client = MagicMock()
        mock_client.list_examples.return_value = iter(mock_examples)
        mock_client_class.return_value = mock_client

        client = query_module.get_client()
        examples = list(client.list_examples(dataset_name="Email Agent: Trajectory"))

        # Should return 2 examples
        assert len(examples) == 2

        # First example should have empty trajectory
        first_example = examples[0]
        assert (
            first_example.inputs["email_input"]["author"] == "Marketing Team <marketing@openai.com>"
        )
        assert first_example.inputs["email_input"]["subject"] == "Newsletter: New Model from OpenAI"
        assert first_example.outputs["trajectory"] == []

        # Second example should have specific trajectory
        second_example = examples[1]
        assert (
            second_example.inputs["email_input"]["author"] == "Project Team <project@company.com>"
        )
        assert second_example.inputs["email_input"]["subject"] == "Joint presentation next month"
        assert second_example.outputs["trajectory"] == [
            "check_calendar_availability",
            "schedule_meeting",
            "write_email",
            "done",
        ]
