"""Parity tests - verify Python and TypeScript scripts produce identical output.

Run with: pytest tests/scripts/langsmith/parity/test_parity.py -v
"""

import json

import pytest

from ..conftest import (
    PY_GENERATE_DATASETS,
    PY_QUERY_DATASETS,
    PY_QUERY_TRACES,
    PY_UPLOAD_EVALUATORS,
    TS_GENERATE_DATASETS,
    TS_QUERY_DATASETS,
    TS_QUERY_TRACES,
    TS_UPLOAD_EVALUATORS,
    create_sample_dataset_json,
    create_sample_trace_jsonl,
    run_python_script,
    run_ts_script,
)


@pytest.fixture
def sample_trace_jsonl(tmp_path):
    """Create a sample JSONL trace file for testing."""
    return create_sample_trace_jsonl(tmp_path)


@pytest.fixture
def sample_dataset_json(tmp_path):
    """Create a sample dataset JSON file for testing."""
    return create_sample_dataset_json(tmp_path)


def normalize_json(data):
    """Normalize JSON data for comparison - sort keys, normalize values."""
    if isinstance(data, dict):
        return {k: normalize_json(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [normalize_json(item) for item in data]
    else:
        return data


def assert_json_equal(py_data, ts_data, msg=""):
    """Assert two JSON structures are equal after normalization."""
    py_normalized = normalize_json(py_data)
    ts_normalized = normalize_json(ts_data)
    assert py_normalized == ts_normalized, (
        f"{msg}\nPython: {py_normalized}\nTypeScript: {ts_normalized}"
    )


class TestCLIHelpParity:
    """Test that Python and TypeScript CLI help output is equivalent."""

    def test_query_traces_help_parity(self):
        """query_traces help output matches."""
        py_result = run_python_script(PY_QUERY_TRACES, ["--help"])
        ts_result = run_ts_script(TS_QUERY_TRACES, ["--help"])

        assert py_result.returncode == 0
        assert ts_result.returncode == 0

        # Both should have same subcommands
        assert "traces" in py_result.stdout.lower()
        assert "traces" in ts_result.stdout.lower()
        assert "runs" in py_result.stdout.lower()
        assert "runs" in ts_result.stdout.lower()

    def test_generate_datasets_help_parity(self):
        """generate_datasets help output matches."""
        py_result = run_python_script(PY_GENERATE_DATASETS, ["--help"])
        ts_result = run_ts_script(TS_GENERATE_DATASETS, ["--help"])

        assert py_result.returncode == 0
        assert ts_result.returncode == 0

        # Both should have same options and types
        for option in ["--input", "--type", "--output"]:
            assert option in py_result.stdout
            assert option in ts_result.stdout

        for dataset_type in ["final_response", "single_step", "trajectory", "rag"]:
            assert dataset_type in py_result.stdout
            assert dataset_type in ts_result.stdout

    def test_query_datasets_help_parity(self):
        """query_datasets help output matches."""
        py_result = run_python_script(PY_QUERY_DATASETS, ["--help"])
        ts_result = run_ts_script(TS_QUERY_DATASETS, ["--help"])

        assert py_result.returncode == 0
        assert ts_result.returncode == 0

        # Both should have same subcommands
        for cmd in ["list-datasets", "show", "view-file", "structure", "export"]:
            assert cmd in py_result.stdout
            assert cmd in ts_result.stdout

    def test_upload_evaluators_help_parity(self):
        """upload_evaluators help output matches."""
        py_result = run_python_script(PY_UPLOAD_EVALUATORS, ["--help"])
        ts_result = run_ts_script(TS_UPLOAD_EVALUATORS, ["--help"])

        assert py_result.returncode == 0
        assert ts_result.returncode == 0

        # Both should have same subcommands
        for cmd in ["list", "upload", "delete"]:
            assert cmd in py_result.stdout.lower()
            assert cmd in ts_result.stdout.lower()


class TestGenerateDatasetsOutputParity:
    """Test that Python and TypeScript produce identical dataset output."""

    def test_trajectory_parity(self, sample_trace_jsonl, tmp_path):
        """Python and TypeScript produce identical trajectory output."""
        py_output = tmp_path / "py_output.json"
        ts_output = tmp_path / "ts_output.json"

        # Run Python
        py_result = run_python_script(
            PY_GENERATE_DATASETS,
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
            TS_GENERATE_DATASETS,
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

        # Compare outputs - exact match
        with open(py_output) as f:
            py_data = json.load(f)
        with open(ts_output) as f:
            ts_data = json.load(f)

        assert len(py_data) == len(ts_data), (
            f"Different number of examples: Python={len(py_data)}, TypeScript={len(ts_data)}"
        )

        # Exact comparison after normalization
        for i, (py_ex, ts_ex) in enumerate(zip(py_data, ts_data, strict=True)):
            assert_json_equal(py_ex, ts_ex, f"Example {i} differs")

    def test_final_response_parity(self, sample_trace_jsonl, tmp_path):
        """Python and TypeScript produce identical final_response output."""
        py_output = tmp_path / "py_final.json"
        ts_output = tmp_path / "ts_final.json"

        # Run Python
        py_result = run_python_script(
            PY_GENERATE_DATASETS,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "final_response",
                "--output",
                str(py_output),
            ],
        )
        assert py_result.returncode == 0, f"Python failed: {py_result.stderr}"

        # Run TypeScript
        ts_result = run_ts_script(
            TS_GENERATE_DATASETS,
            [
                "--input",
                str(sample_trace_jsonl),
                "--type",
                "final_response",
                "--output",
                str(ts_output),
            ],
        )
        assert ts_result.returncode == 0, f"TypeScript failed: {ts_result.stderr}"

        # Compare outputs - exact match
        with open(py_output) as f:
            py_data = json.load(f)
        with open(ts_output) as f:
            ts_data = json.load(f)

        assert len(py_data) == len(ts_data), (
            f"Different number of examples: Python={len(py_data)}, TypeScript={len(ts_data)}"
        )

        for i, (py_ex, ts_ex) in enumerate(zip(py_data, ts_data, strict=True)):
            assert_json_equal(py_ex, ts_ex, f"Example {i} differs")


class TestQueryDatasetsOutputParity:
    """Test that Python and TypeScript produce identical query output."""

    def test_view_file_json_parity(self, sample_dataset_json):
        """Python and TypeScript view-file JSON output is identical."""
        py_result = run_python_script(
            PY_QUERY_DATASETS,
            ["view-file", str(sample_dataset_json), "--limit", "2", "--format", "json"],
        )
        ts_result = run_ts_script(
            TS_QUERY_DATASETS,
            ["view-file", str(sample_dataset_json), "--limit", "2", "--format", "json"],
        )

        assert py_result.returncode == 0, f"Python failed: {py_result.stderr}"
        assert ts_result.returncode == 0, f"TypeScript failed: {ts_result.stderr}"

        # Extract JSON from output (may have other text before/after)
        py_json_start = py_result.stdout.find("[")
        py_json_end = py_result.stdout.rfind("]") + 1
        ts_json_start = ts_result.stdout.find("[")
        ts_json_end = ts_result.stdout.rfind("]") + 1

        assert py_json_start >= 0, "Python output doesn't contain JSON array"
        assert ts_json_start >= 0, "TypeScript output doesn't contain JSON array"

        py_data = json.loads(py_result.stdout[py_json_start:py_json_end])
        ts_data = json.loads(ts_result.stdout[ts_json_start:ts_json_end])

        assert_json_equal(py_data, ts_data, "view-file JSON output differs")

    def test_structure_parity(self, sample_dataset_json):
        """Python and TypeScript structure produce equivalent info."""
        py_result = run_python_script(
            PY_QUERY_DATASETS,
            ["structure", str(sample_dataset_json)],
        )
        ts_result = run_ts_script(
            TS_QUERY_DATASETS,
            ["structure", str(sample_dataset_json)],
        )

        assert py_result.returncode == 0
        assert ts_result.returncode == 0

        # Both should identify JSON format
        assert "JSON" in py_result.stdout, f"Python output: {py_result.stdout}"
        assert "JSON" in ts_result.stdout, f"TypeScript output: {ts_result.stdout}"

        # Both should show example count (2 examples)
        assert "2" in py_result.stdout, f"Python should show 2 examples: {py_result.stdout}"
        assert "2" in ts_result.stdout, f"TypeScript should show 2 examples: {ts_result.stdout}"
