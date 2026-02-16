"""Tests for langsmith-trace Python scripts (query_traces.py).

Run with: pytest tests/scripts/langsmith_trace/test_python.py -v
"""

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from ..conftest import PY_QUERY_TRACES, SCRIPTS_BASE, run_python_script
from ..fixtures import SAMPLE_RUNS_WITH_METADATA, SAMPLE_TRACE_GET, SAMPLE_TRACES_LIST


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


# =============================================================================
# Mocked API Tests - Using direct function imports
# =============================================================================


@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict(os.environ, {
        "LANGSMITH_API_KEY": "test-api-key-12345",
        "LANGSMITH_PROJECT": "test-project",
    }):
        yield


@pytest.fixture
def query_module(mock_env):
    """Import the query_traces module with mocked env."""
    # Add script directory to path
    script_dir = SCRIPTS_BASE / "langsmith_trace-py" / "scripts"
    sys.path.insert(0, str(script_dir))

    # Clear any cached imports
    if "query_traces" in sys.modules:
        del sys.modules["query_traces"]

    try:
        import query_traces
        yield query_traces
    finally:
        sys.path.remove(str(script_dir))
        if "query_traces" in sys.modules:
            del sys.modules["query_traces"]


def create_mock_run(run_data: dict) -> MagicMock:
    """Create a mock Run object from dict data."""
    mock = MagicMock()
    mock.id = run_data.get("run_id")
    mock.trace_id = run_data.get("trace_id")
    mock.name = run_data.get("name")
    mock.run_type = run_data.get("run_type")
    mock.parent_run_id = run_data.get("parent_run_id")

    # Parse timestamps
    start_time = run_data.get("start_time")
    end_time = run_data.get("end_time")
    if start_time:
        mock.start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    else:
        mock.start_time = None
    if end_time:
        mock.end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    else:
        mock.end_time = None

    mock.inputs = run_data.get("inputs", {})
    mock.outputs = run_data.get("outputs", {})
    mock.status = run_data.get("status", "success")
    mock.error = run_data.get("error")
    mock.extra = run_data.get("custom_metadata", {})
    return mock


class TestMockedAPIFunctions:
    """Test API functions with mocked LangSmith client."""

    def test_get_client(self, query_module):
        """get_client returns a client when API key is set."""
        client = query_module.get_client()
        assert client is not None

    def test_build_query_params_basic(self, query_module):
        """build_query_params creates correct params."""
        params = query_module.build_query_params(
            project="my-project",
            trace_ids=None,
            limit=10,
            last_n_minutes=None,
            since=None,
            run_type=None,
            is_root=True,
            error=None,
            name=None,
            raw_filter=None,
        )

        assert params["project_name"] == "my-project"
        assert params["limit"] == 10
        assert params["is_root"] is True

    def test_build_query_params_with_run_type(self, query_module):
        """build_query_params handles run type filter."""
        params = query_module.build_query_params(
            project="my-project",
            trace_ids=None,
            limit=5,
            last_n_minutes=None,
            since=None,
            run_type="llm",
            is_root=False,
            error=None,
            name=None,
            raw_filter=None,
        )

        assert params["project_name"] == "my-project"
        assert params["limit"] == 5
        assert params["run_type"] == "llm"
        # is_root is only included when True (to filter to root runs only)
        assert "is_root" not in params

    def test_build_query_params_with_error_filter(self, query_module):
        """build_query_params handles error filter."""
        params = query_module.build_query_params(
            project="my-project",
            trace_ids=None,
            limit=10,
            last_n_minutes=None,
            since=None,
            run_type=None,
            is_root=True,
            error=True,
            name=None,
            raw_filter=None,
        )

        assert params["error"] is True


class TestMockedAPIWithFixtures:
    """Test that mocked API returns data matching our fixtures."""

    @patch("query_traces.Client")
    def test_trace_list_returns_expected_data(self, mock_client_class, query_module):
        """Verify list output matches SAMPLE_TRACES_LIST format."""
        mock_runs = [create_mock_run(t) for t in SAMPLE_TRACES_LIST]

        mock_client = MagicMock()
        mock_client.list_runs.return_value = iter(mock_runs)
        mock_client_class.return_value = mock_client

        client = query_module.get_client()
        runs = list(client.list_runs(project_name="test", limit=3, is_root=True))

        # Should return 3 traces
        assert len(runs) == 3

        # First trace should match fixture
        assert runs[0].name == "LangGraph"
        assert runs[0].run_type == "chain"
        assert runs[0].parent_run_id is None

        # Second trace
        assert runs[1].name == "LangGraph"
        assert runs[1].trace_id == "019c62bb-92cc-71b0-97e7-8e2b283a432c"

        # Third trace
        assert runs[2].name == "LangGraph"
        assert runs[2].trace_id == "019c62bb-695f-70e2-a62a-e8fec7118137"

    @patch("query_traces.Client")
    def test_trace_get_returns_full_hierarchy(self, mock_client_class, query_module):
        """Verify get output matches SAMPLE_TRACE_GET format."""
        # Create mock runs for the full trace hierarchy
        mock_runs = [create_mock_run(r) for r in SAMPLE_TRACE_GET["runs"]]

        mock_client = MagicMock()
        mock_client.list_runs.return_value = iter(mock_runs)
        mock_client_class.return_value = mock_client

        client = query_module.get_client()
        trace_id = SAMPLE_TRACE_GET["trace_id"]
        runs = list(client.list_runs(trace_id=trace_id))

        # Should return 7 runs in the trace
        assert len(runs) == 7

        # Check all expected run names are present
        run_names = [r.name for r in runs]
        assert "LangGraph" in run_names
        assert "ChatAnthropic" in run_names
        assert "calculator" in run_names
        assert "tools" in run_names
        assert "model" in run_names

        # Check run types match fixture
        run_types = {r.name: r.run_type for r in runs}
        assert run_types["LangGraph"] == "chain"
        assert run_types["ChatAnthropic"] == "llm"
        assert run_types["calculator"] == "tool"

    @patch("query_traces.Client")
    def test_runs_with_metadata_includes_all_fields(self, mock_client_class, query_module):
        """Verify runs with metadata match SAMPLE_RUNS_WITH_METADATA format."""
        mock_runs = [create_mock_run(r) for r in SAMPLE_RUNS_WITH_METADATA]

        # Add extra metadata fields to mocks
        for mock, data in zip(mock_runs, SAMPLE_RUNS_WITH_METADATA, strict=True):
            mock.extra = {"metadata": data.get("custom_metadata", {})}

        mock_client = MagicMock()
        mock_client.list_runs.return_value = iter(mock_runs)
        mock_client_class.return_value = mock_client

        client = query_module.get_client()
        runs = list(client.list_runs(project_name="test", limit=3))

        # Should return 3 runs
        assert len(runs) == 3

        # First run should have LLM metadata
        assert runs[0].name == "ChatAnthropic"
        assert runs[0].run_type == "llm"

        # Check metadata is present
        assert "metadata" in runs[0].extra
        assert "ls_model_name" in runs[0].extra["metadata"]
        assert runs[0].extra["metadata"]["ls_model_name"] == "claude-3-5-haiku-20241022"
