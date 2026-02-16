"""Tests for langsmith-dataset Python scripts (generate_datasets.py, query_datasets.py).

Run with: pytest tests/scripts/langsmith/langsmith_dataset/test_python.py -v
"""

import json

import pytest

from ..conftest import PY_GENERATE_DATASETS, PY_QUERY_DATASETS, run_python_script
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
# Fixture validation
# =============================================================================


class TestRealDataStructureValidation:
    """Validate that our fixtures match real API structures with exact assertions."""

    def test_dataset_structure(self):
        """Verify SAMPLE_DATASETS has correct structure and exact values."""
        assert len(SAMPLE_DATASETS) == 4

        # Check specific datasets exist with exact names
        dataset_names = [d["name"] for d in SAMPLE_DATASETS]
        assert "shipping-support-golden" in dataset_names
        assert "Email Agent Notebook: Trajectory" in dataset_names
        assert "Email Agent: Trajectory" in dataset_names
        assert "kb-agent-golden-set" in dataset_names

        # Check exact example counts
        dataset_counts = {d["name"]: d["example_count"] for d in SAMPLE_DATASETS}
        assert dataset_counts["shipping-support-golden"] == 10
        assert dataset_counts["Email Agent Notebook: Trajectory"] == 5
        assert dataset_counts["Email Agent: Trajectory"] == 16
        assert dataset_counts["kb-agent-golden-set"] == 15

        # Verify all datasets have required fields
        for dataset in SAMPLE_DATASETS:
            assert "name" in dataset
            assert "id" in dataset
            assert "example_count" in dataset

    def test_dataset_examples_structure(self):
        """Verify SAMPLE_DATASET_EXAMPLES has correct structure and exact values."""
        assert len(SAMPLE_DATASET_EXAMPLES) == 2

        # First example should have empty trajectory
        first_example = SAMPLE_DATASET_EXAMPLES[0]
        assert first_example["inputs"]["email_input"]["author"] == "Marketing Team <marketing@openai.com>"
        assert first_example["inputs"]["email_input"]["subject"] == "Newsletter: New Model from OpenAI"
        assert first_example["outputs"]["trajectory"] == []

        # Second example should have specific trajectory
        second_example = SAMPLE_DATASET_EXAMPLES[1]
        assert second_example["inputs"]["email_input"]["author"] == "Project Team <project@company.com>"
        assert second_example["inputs"]["email_input"]["subject"] == "Joint presentation next month"
        assert second_example["outputs"]["trajectory"] == [
            "check_calendar_availability",
            "schedule_meeting",
            "write_email",
            "done",
        ]
