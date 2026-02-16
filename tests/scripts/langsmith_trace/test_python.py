"""Tests for langsmith-trace Python scripts (query_traces.py).

Run with: pytest tests/scripts/langsmith/langsmith-trace/test_python.py -v
"""

import pytest

from ..conftest import run_python_script, PY_QUERY_TRACES
from ..fixtures import SAMPLE_TRACES_LIST, SAMPLE_TRACE_GET


@pytest.fixture
def script_path():
    """Path to query_traces.py."""
    return PY_QUERY_TRACES


class TestCLIHelp:
    """Test CLI help output."""

    def test_main_help(self, script_path):
        """Provides main help output."""
        result = run_python_script(script_path, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "traces" in result.stdout.lower()
        assert "runs" in result.stdout.lower()

    def test_traces_list_help(self, script_path):
        """traces list subcommand help."""
        result = run_python_script(script_path, ["traces", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--limit" in result.stdout
        assert "--project" in result.stdout

    def test_traces_get_help(self, script_path):
        """traces get subcommand help."""
        result = run_python_script(script_path, ["traces", "get", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"

    def test_traces_export_help(self, script_path):
        """traces export subcommand help."""
        result = run_python_script(script_path, ["traces", "export", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"

    def test_runs_list_help(self, script_path):
        """runs list subcommand help."""
        result = run_python_script(script_path, ["runs", "list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--run-type" in result.stdout


class TestRealDataStructureValidation:
    """Validate that our fixtures match real API structures with exact assertions."""

    def test_trace_list_structure(self):
        """Verify SAMPLE_TRACES_LIST has correct structure and exact values."""
        assert len(SAMPLE_TRACES_LIST) == 3

        # Check first trace exact values
        first_trace = SAMPLE_TRACES_LIST[0]
        assert first_trace["run_id"] == "019c62bb-d608-74c3-88bd-54d51db3d4a7"
        assert first_trace["trace_id"] == "019c62bb-d608-74c3-88bd-54d51db3d4a7"
        assert first_trace["name"] == "LangGraph"
        assert first_trace["run_type"] == "chain"
        assert first_trace["parent_run_id"] is None
        assert first_trace["start_time"] == "2026-02-15T19:16:43.144899"
        assert first_trace["end_time"] == "2026-02-15T19:16:46.686558"

        # Verify all traces have required fields
        for trace in SAMPLE_TRACES_LIST:
            assert "run_id" in trace
            assert "trace_id" in trace
            assert "name" in trace
            assert "run_type" in trace
            assert len(trace["run_id"]) == 36  # UUID format

    def test_trace_get_structure(self):
        """Verify SAMPLE_TRACE_GET has correct structure and exact values."""
        assert SAMPLE_TRACE_GET["trace_id"] == "019c62bb-d608-74c3-88bd-54d51db3d4a7"
        assert SAMPLE_TRACE_GET["run_count"] == 7
        assert len(SAMPLE_TRACE_GET["runs"]) == 7

        # Check specific runs exist with exact values
        run_names = [r["name"] for r in SAMPLE_TRACE_GET["runs"]]
        assert "LangGraph" in run_names
        assert "ChatAnthropic" in run_names
        assert "calculator" in run_names
        assert "tools" in run_names
        assert "model" in run_names

        # Check run types
        run_types = {r["name"]: r["run_type"] for r in SAMPLE_TRACE_GET["runs"]}
        assert run_types["LangGraph"] == "chain"
        assert run_types["ChatAnthropic"] == "llm"
        assert run_types["calculator"] == "tool"

        # Check parent hierarchy (calculator -> tools -> LangGraph)
        calculator_run = next(r for r in SAMPLE_TRACE_GET["runs"] if r["name"] == "calculator")
        tools_run = next(r for r in SAMPLE_TRACE_GET["runs"] if r["name"] == "tools")
        assert calculator_run["parent_run_id"] == tools_run["run_id"]
        assert tools_run["parent_run_id"] == SAMPLE_TRACE_GET["trace_id"]
