"""Test local file operations (no API credentials required).

These tests verify that Python and TypeScript scripts produce consistent
output when processing local files.
"""

import json
import tempfile
from pathlib import Path

import pytest

from .conftest import run_python_script, run_ts_script


@pytest.fixture
def sample_trace_jsonl(tmp_path):
    """Create a sample JSONL trace file for testing."""
    trace_data = [
        {
            "run_id": "run-001",
            "trace_id": "trace-001",
            "name": "agent",
            "run_type": "chain",
            "parent_run_id": None,
            "start_time": "2025-01-15T10:00:00Z",
            "end_time": "2025-01-15T10:00:05Z",
            "inputs": {"query": "What is the capital of France?"},
            "outputs": {"answer": "Paris"},
        },
        {
            "run_id": "run-002",
            "trace_id": "trace-001",
            "name": "search_tool",
            "run_type": "tool",
            "parent_run_id": "run-001",
            "start_time": "2025-01-15T10:00:01Z",
            "end_time": "2025-01-15T10:00:02Z",
            "inputs": {"query": "capital France"},
            "outputs": {"result": "Paris is the capital"},
        },
        {
            "run_id": "run-003",
            "trace_id": "trace-001",
            "name": "llm",
            "run_type": "llm",
            "parent_run_id": "run-001",
            "start_time": "2025-01-15T10:00:03Z",
            "end_time": "2025-01-15T10:00:04Z",
            "inputs": {"messages": [{"role": "user", "content": "summarize"}]},
            "outputs": {"answer": "Paris"},
        },
    ]

    jsonl_file = tmp_path / "trace-001.jsonl"
    with open(jsonl_file, "w") as f:
        for run in trace_data:
            f.write(json.dumps(run) + "\n")

    return jsonl_file


@pytest.fixture
def sample_dataset_json(tmp_path):
    """Create a sample dataset JSON file for testing."""
    dataset = [
        {
            "trace_id": "trace-001",
            "inputs": {"query": "What is the capital of France?"},
            "outputs": {"expected_response": "Paris"},
        },
        {
            "trace_id": "trace-002",
            "inputs": {"query": "What is 2 + 2?"},
            "outputs": {"expected_response": "4"},
        },
    ]

    json_file = tmp_path / "dataset.json"
    with open(json_file, "w") as f:
        json.dump(dataset, f, indent=2)

    return json_file


class TestGenerateDatasetsLocal:
    """Test generate_datasets with local files."""

    def test_python_generates_trajectory(self, py_generate_datasets, sample_trace_jsonl, tmp_path):
        """Python generates trajectory dataset from JSONL."""
        output_file = tmp_path / "output.json"
        result = run_python_script(
            py_generate_datasets,
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

        assert len(data) > 0
        # Check trajectory structure
        assert "trace_id" in data[0]
        assert "inputs" in data[0]
        assert "outputs" in data[0]
        assert "expected_trajectory" in data[0]["outputs"]

    def test_ts_generates_trajectory(self, ts_generate_datasets, sample_trace_jsonl, tmp_path):
        """TypeScript generates trajectory dataset from JSONL."""
        output_file = tmp_path / "output.json"
        result = run_ts_script(
            ts_generate_datasets,
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

        assert len(data) > 0
        # Check trajectory structure
        assert "trace_id" in data[0]
        assert "inputs" in data[0]
        assert "outputs" in data[0]
        assert "expected_trajectory" in data[0]["outputs"]

    def test_trajectory_parity(self, py_generate_datasets, ts_generate_datasets, sample_trace_jsonl, tmp_path):
        """Python and TypeScript produce same trajectory output."""
        py_output = tmp_path / "py_output.json"
        ts_output = tmp_path / "ts_output.json"

        # Run Python
        py_result = run_python_script(
            py_generate_datasets,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "trajectory",
                "--output",
                str(py_output),
            ],
        )
        assert py_result.returncode == 0, f"Python failed: {py_result.stderr}"

        # Run TypeScript
        ts_result = run_ts_script(
            ts_generate_datasets,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "trajectory",
                "--output",
                str(ts_output),
            ],
        )
        assert ts_result.returncode == 0, f"TypeScript failed: {ts_result.stderr}"

        # Compare outputs
        with open(py_output) as f:
            py_data = json.load(f)
        with open(ts_output) as f:
            ts_data = json.load(f)

        assert len(py_data) == len(ts_data), "Different number of examples"

        # Compare structure (not exact values due to potential ordering differences)
        for py_ex, ts_ex in zip(py_data, ts_data):
            assert py_ex["trace_id"] == ts_ex["trace_id"]
            assert "expected_trajectory" in py_ex["outputs"]
            assert "expected_trajectory" in ts_ex["outputs"]
            # Tool names should match
            assert set(py_ex["outputs"]["expected_trajectory"]) == set(
                ts_ex["outputs"]["expected_trajectory"]
            )

    def test_python_generates_final_response(
        self, py_generate_datasets, sample_trace_jsonl, tmp_path
    ):
        """Python generates final_response dataset."""
        output_file = tmp_path / "output.json"
        result = run_python_script(
            py_generate_datasets,
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

    def test_ts_generates_final_response(
        self, ts_generate_datasets, sample_trace_jsonl, tmp_path
    ):
        """TypeScript generates final_response dataset."""
        output_file = tmp_path / "output.json"
        result = run_ts_script(
            ts_generate_datasets,
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


class TestQueryDatasetsLocal:
    """Test query_datasets with local files."""

    def test_python_view_file(self, py_query_datasets, sample_dataset_json):
        """Python view-file command works."""
        result = run_python_script(
            py_query_datasets,
            ["view-file", str(sample_dataset_json), "--limit", "1", "--format", "json"],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        # Should output valid JSON
        output = result.stdout.strip()
        # Find JSON in output (may have prefix text)
        assert "[" in output  # JSON array

    def test_ts_view_file(self, ts_query_datasets, sample_dataset_json):
        """TypeScript view-file command works."""
        result = run_ts_script(
            ts_query_datasets,
            ["view-file", str(sample_dataset_json), "--limit", "1", "--format", "json"],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        # Should output valid JSON
        output = result.stdout.strip()
        assert "[" in output  # JSON array

    def test_python_structure(self, py_query_datasets, sample_dataset_json):
        """Python structure command works."""
        result = run_python_script(
            py_query_datasets,
            ["structure", str(sample_dataset_json)],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "JSON" in result.stdout
        assert "Examples" in result.stdout or "2" in result.stdout

    def test_ts_structure(self, ts_query_datasets, sample_dataset_json):
        """TypeScript structure command works."""
        result = run_ts_script(
            ts_query_datasets,
            ["structure", str(sample_dataset_json)],
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "JSON" in result.stdout
        assert "Examples" in result.stdout or "2" in result.stdout
