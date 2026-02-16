"""Test that all scripts provide valid --help output.

These tests verify basic CLI functionality without requiring API credentials.
"""

import pytest

from .conftest import run_python_script, run_ts_script


class TestQueryTracesHelp:
    """Test query_traces --help output."""

    def test_python_help(self, py_query_traces):
        """Python script provides help output."""
        result = run_python_script(py_query_traces, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "traces" in result.stdout.lower()
        assert "runs" in result.stdout.lower()

    def test_ts_help(self, ts_query_traces):
        """TypeScript script provides help output."""
        result = run_ts_script(ts_query_traces, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "traces" in result.stdout.lower()
        assert "runs" in result.stdout.lower()

    def test_python_traces_list_help(self, py_query_traces):
        """Python traces list subcommand help."""
        result = run_python_script(py_query_traces, ["traces", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--limit" in result.stdout
        assert "--project" in result.stdout

    def test_ts_traces_list_help(self, ts_query_traces):
        """TypeScript traces list subcommand help."""
        result = run_ts_script(ts_query_traces, ["traces", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--limit" in result.stdout
        assert "--project" in result.stdout

    def test_python_runs_list_help(self, py_query_traces):
        """Python runs list subcommand help."""
        result = run_python_script(py_query_traces, ["runs", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--run-type" in result.stdout

    def test_ts_runs_list_help(self, ts_query_traces):
        """TypeScript runs list subcommand help."""
        result = run_ts_script(ts_query_traces, ["runs", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--run-type" in result.stdout


class TestGenerateDatasetsHelp:
    """Test generate_datasets --help output."""

    def test_python_help(self, py_generate_datasets):
        """Python script provides help output."""
        result = run_python_script(py_generate_datasets, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--input" in result.stdout
        assert "--type" in result.stdout
        assert "--output" in result.stdout

    def test_ts_help(self, ts_generate_datasets):
        """TypeScript script provides help output."""
        result = run_ts_script(ts_generate_datasets, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--input" in result.stdout
        assert "--type" in result.stdout
        assert "--output" in result.stdout

    def test_python_has_dataset_types(self, py_generate_datasets):
        """Python help mentions all dataset types."""
        result = run_python_script(py_generate_datasets, ["--help"])
        assert result.returncode == 0
        assert "final_response" in result.stdout
        assert "single_step" in result.stdout
        assert "trajectory" in result.stdout
        assert "rag" in result.stdout

    def test_ts_has_dataset_types(self, ts_generate_datasets):
        """TypeScript help mentions all dataset types."""
        result = run_ts_script(ts_generate_datasets, ["--help"])
        assert result.returncode == 0
        assert "final_response" in result.stdout
        assert "single_step" in result.stdout
        assert "trajectory" in result.stdout
        assert "rag" in result.stdout


class TestQueryDatasetsHelp:
    """Test query_datasets --help output."""

    def test_python_help(self, py_query_datasets):
        """Python script provides help output."""
        result = run_python_script(py_query_datasets, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()

    def test_ts_help(self, ts_query_datasets):
        """TypeScript script provides help output."""
        result = run_ts_script(ts_query_datasets, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()

    def test_python_subcommands(self, py_query_datasets):
        """Python has expected subcommands."""
        result = run_python_script(py_query_datasets, ["--help"])
        assert result.returncode == 0
        assert "list-datasets" in result.stdout
        assert "show" in result.stdout
        assert "view-file" in result.stdout
        assert "structure" in result.stdout
        assert "export" in result.stdout

    def test_ts_subcommands(self, ts_query_datasets):
        """TypeScript has expected subcommands."""
        result = run_ts_script(ts_query_datasets, ["--help"])
        assert result.returncode == 0
        assert "list-datasets" in result.stdout
        assert "show" in result.stdout
        assert "view-file" in result.stdout
        assert "structure" in result.stdout
        assert "export" in result.stdout


class TestUploadEvaluatorsHelp:
    """Test upload_evaluators --help output."""

    def test_python_help(self, py_upload_evaluators):
        """Python script provides help output."""
        result = run_python_script(py_upload_evaluators, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()
        assert "upload" in result.stdout.lower()
        assert "delete" in result.stdout.lower()

    def test_ts_help(self, ts_upload_evaluators):
        """TypeScript script provides help output."""
        result = run_ts_script(ts_upload_evaluators, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()
        assert "upload" in result.stdout.lower()
        assert "delete" in result.stdout.lower()

    def test_python_upload_help(self, py_upload_evaluators):
        """Python upload subcommand help."""
        result = run_python_script(py_upload_evaluators, ["upload", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--name" in result.stdout
        assert "--function" in result.stdout

    def test_ts_upload_help(self, ts_upload_evaluators):
        """TypeScript upload subcommand help."""
        result = run_ts_script(ts_upload_evaluators, ["upload", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--name" in result.stdout
        assert "--function" in result.stdout
