"""Unit tests for external_data_handler module with mocked LangSmith client."""

import json
from unittest.mock import MagicMock, patch

import pytest

from scaffold.python.external_data_handler import (
    HANDLERS,
    _parse_ts,
    _replay_trace_operations,
    cleanup_namespace,
    run_handler,
    run_task_handlers,
    upload_datasets,
    upload_traces,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_client():
    """Create a mock LangSmith client."""
    client = MagicMock()
    client.create_run = MagicMock()
    client.update_run = MagicMock()
    client.flush = MagicMock()
    client.create_dataset = MagicMock(return_value=MagicMock(id="dataset-123"))
    client.create_examples = MagicMock()
    client.list_projects = MagicMock(return_value=[])
    client.list_datasets = MagicMock(return_value=[])
    client.delete_project = MagicMock()
    client.delete_dataset = MagicMock()
    return client


@pytest.fixture
def trace_data_dir(tmp_path):
    """Create a temp directory with trace fixture files."""
    trace_file = tmp_path / "trace_001.jsonl"
    operations = [
        {
            "operation": "post",
            "id": "run-001",
            "name": "root_run",
            "run_type": "chain",
            "inputs": {"messages": [{"content": "Hello world"}]},
            "start_time": "2024-01-01T00:00:00Z",
            "parent_run_id": None,
        },
        {
            "operation": "post",
            "id": "run-002",
            "name": "child_run",
            "run_type": "llm",
            "inputs": {},
            "start_time": "2024-01-01T00:00:01Z",
            "parent_run_id": "run-001",
        },
        {
            "operation": "patch",
            "id": "run-002",
            "end_time": "2024-01-01T00:00:02Z",
            "outputs": {"result": "success"},
        },
        {
            "operation": "patch",
            "id": "run-001",
            "end_time": "2024-01-01T00:00:03Z",
            "outputs": {"answer": "Hello!"},
        },
    ]
    trace_file.write_text("\n".join(json.dumps(op) for op in operations))
    return tmp_path


@pytest.fixture
def dataset_data_dir(tmp_path):
    """Create a temp directory with dataset files."""
    # SQL dataset
    sql_file = tmp_path / "sql_agent_dataset.json"
    sql_file.write_text(
        json.dumps(
            [
                {"inputs": {"query": "SELECT * FROM users"}, "outputs": {"result": []}},
                {"inputs": {"query": "SELECT COUNT(*)"}, "outputs": {"result": [10]}},
            ]
        )
    )

    # Trajectory dataset
    traj_file = tmp_path / "trajectory_dataset.json"
    traj_file.write_text(json.dumps([{"inputs": {"x": 1}, "outputs": {"y": 2}}]))

    return tmp_path


# =============================================================================
# _parse_ts TESTS
# =============================================================================


class TestParseTs:
    def test_iso_with_z(self):
        result = _parse_ts("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.tzinfo is not None

    def test_iso_with_offset(self):
        result = _parse_ts("2024-01-15T10:30:00+05:00")
        assert result is not None
        assert result.tzinfo is not None

    def test_empty_string(self):
        assert _parse_ts("") is None

    def test_invalid_string(self):
        assert _parse_ts("not a date") is None


# =============================================================================
# _replay_trace_operations TESTS
# =============================================================================


class TestReplayTraceOperations:
    def test_replays_post_and_patch(self, mock_client):
        operations = [
            {
                "operation": "post",
                "id": "old-id-1",
                "name": "root",
                "run_type": "chain",
                "inputs": {},
                "start_time": "2024-01-01T00:00:00Z",
            },
            {
                "operation": "patch",
                "id": "old-id-1",
                "end_time": "2024-01-01T00:00:01Z",
                "outputs": {"done": True},
            },
        ]

        result = _replay_trace_operations(mock_client, "test-project", operations)

        assert result is not None  # Returns new root ID
        assert mock_client.create_run.called
        assert mock_client.update_run.called

    def test_maps_parent_ids(self, mock_client):
        operations = [
            {
                "operation": "post",
                "id": "parent-id",
                "name": "parent",
                "run_type": "chain",
                "inputs": {},
                "start_time": "2024-01-01T00:00:00Z",
            },
            {
                "operation": "post",
                "id": "child-id",
                "name": "child",
                "run_type": "llm",
                "inputs": {},
                "start_time": "2024-01-01T00:00:01Z",
                "parent_run_id": "parent-id",
            },
        ]

        _replay_trace_operations(mock_client, "test-project", operations)

        # Should have called create_run twice
        assert mock_client.create_run.call_count == 2

        # Child's parent_run_id should be mapped to new parent ID
        child_call = mock_client.create_run.call_args_list[1]
        assert child_call.kwargs.get("parent_run_id") is not None

    def test_returns_none_for_empty_operations(self, mock_client):
        result = _replay_trace_operations(mock_client, "test-project", [])
        assert result is None

    def test_returns_none_for_no_post_operations(self, mock_client):
        operations = [{"operation": "patch", "id": "x", "outputs": {}}]
        result = _replay_trace_operations(mock_client, "test-project", operations)
        assert result is None


# =============================================================================
# upload_traces TESTS
# =============================================================================


class TestUploadTraces:
    def test_uploads_traces_from_jsonl(self, mock_client, trace_data_dir):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = upload_traces("test-project", trace_data_dir)

        assert mock_client.create_run.called
        assert mock_client.flush.called
        # Should return mapping of old ID to new ID
        assert "run-001" in result

    def test_handles_missing_client(self, trace_data_dir):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(None, "No API key"),
        ):
            result = upload_traces("test-project", trace_data_dir)

        assert result == {}

    def test_handles_empty_directory(self, mock_client, tmp_path):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = upload_traces("test-project", tmp_path)

        assert result == {}
        assert not mock_client.create_run.called


# =============================================================================
# upload_datasets TESTS
# =============================================================================


class TestUploadDatasets:
    def test_uploads_datasets_with_naming_convention(self, mock_client, dataset_data_dir):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = upload_datasets(dataset_data_dir, run_id="abc123")

        # Should create datasets for both files
        assert mock_client.create_dataset.call_count == 2
        assert mock_client.create_examples.call_count == 2

        # Check naming convention: bench-{type}-{run_id}
        assert "sql_agent_dataset.json" in result
        assert result["sql_agent_dataset.json"] == "bench-sql-abc123"
        assert "trajectory_dataset.json" in result
        assert result["trajectory_dataset.json"] == "bench-trajectory-abc123"

    def test_handles_missing_client(self, dataset_data_dir):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(None, "No API key"),
        ):
            result = upload_datasets(dataset_data_dir, run_id="abc123")

        assert result == {}

    def test_handles_single_example(self, mock_client, tmp_path):
        # Single example (not a list)
        single_file = tmp_path / "test_dataset.json"
        single_file.write_text(json.dumps({"inputs": {"x": 1}, "outputs": {"y": 2}}))

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            upload_datasets(tmp_path, run_id="xyz")

        assert mock_client.create_dataset.called
        # Should wrap single example in list
        call_args = mock_client.create_examples.call_args
        assert call_args.kwargs["inputs"] == [{"x": 1}]


# =============================================================================
# cleanup_namespace TESTS
# =============================================================================


class TestCleanupNamespace:
    def test_deletes_matching_projects_and_datasets(self, mock_client):
        # Setup mock to return resources that match
        # Note: MagicMock(name=...) uses 'name' internally, so set .name attribute separately
        mock_project1 = MagicMock()
        mock_project1.name = "bench-test-run123"
        mock_project2 = MagicMock()
        mock_project2.name = "other-project"
        mock_dataset1 = MagicMock()
        mock_dataset1.name = "bench-sql-run123"
        mock_dataset2 = MagicMock()
        mock_dataset2.name = "unrelated-dataset"

        mock_client.list_projects.return_value = [mock_project1, mock_project2]
        mock_client.list_datasets.return_value = [mock_dataset1, mock_dataset2]

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = cleanup_namespace("run123")

        # Should only delete resources ending with -run123
        assert mock_client.delete_project.call_count == 1
        assert mock_client.delete_dataset.call_count == 1
        assert "bench-test-run123" in result["projects"]
        assert "bench-sql-run123" in result["datasets"]

    def test_handles_no_matching_resources(self, mock_client):
        mock_client.list_projects.return_value = []
        mock_client.list_datasets.return_value = []

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = cleanup_namespace("nonexistent")

        assert result == {"projects": [], "datasets": []}

    def test_handles_missing_client(self):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(None, "No API key"),
        ):
            result = cleanup_namespace("run123")

        assert result == {}


# =============================================================================
# run_handler TESTS
# =============================================================================


class TestRunHandler:
    def test_runs_registered_handler(self, mock_client, tmp_path):
        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            # cleanup_namespace is simplest to test
            result = run_handler("cleanup_namespace", run_id="test123")

        assert isinstance(result, dict)

    def test_raises_for_unknown_handler(self):
        with pytest.raises(ValueError, match="Unknown handler"):
            run_handler("nonexistent_handler")

    def test_all_handlers_registered(self):
        assert "upload_traces" in HANDLERS
        assert "upload_datasets" in HANDLERS
        assert "cleanup_namespace" in HANDLERS


# =============================================================================
# run_task_handlers TESTS
# =============================================================================


class TestRunTaskHandlers:
    def test_runs_matching_handlers(self, mock_client, trace_data_dir):
        # Create a mock DataHandler
        handler = MagicMock()
        handler.pattern = "trace_*.jsonl"
        handler.handler = "upload_traces"
        handler.args = {}

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = run_task_handlers(
                [handler], trace_data_dir, project="test-project", run_id="abc"
            )

        assert mock_client.create_run.called
        # upload_traces returns trace ID mapping
        assert isinstance(result, dict)

    def test_skips_handlers_with_no_matching_files(self, mock_client, tmp_path):
        handler = MagicMock()
        handler.pattern = "nonexistent_*.json"
        handler.handler = "upload_traces"
        handler.args = {}

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = run_task_handlers([handler], tmp_path, project="test", run_id="abc")

        assert not mock_client.create_run.called
        assert result == {}

    def test_handles_nonexistent_data_dir(self, mock_client, tmp_path):
        handler = MagicMock()
        handler.pattern = "*.json"
        handler.handler = "upload_traces"

        nonexistent = tmp_path / "does_not_exist"
        result = run_task_handlers([handler], nonexistent, project="test", run_id="abc")

        assert result == {}

    def test_passes_handler_args(self, mock_client, dataset_data_dir):
        handler = MagicMock()
        handler.pattern = "*_dataset.json"
        handler.handler = "upload_datasets"
        handler.args = {"extra_arg": "value"}

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            run_task_handlers([handler], dataset_data_dir, project="test", run_id="xyz")

        assert mock_client.create_dataset.called


# =============================================================================
# REGRESSION TESTS - Verify incorrect implementations would fail
# =============================================================================


class TestRegressionCases:
    """Tests that verify incorrect implementations would fail."""

    def test_upload_traces_requires_post_operations(self, mock_client, tmp_path):
        """Verify upload fails gracefully with no post operations."""
        # Create trace file with only patch operations (no post)
        trace_file = tmp_path / "trace_001.jsonl"
        operations = [
            {"operation": "patch", "id": "run-001", "outputs": {"result": "done"}},
        ]
        trace_file.write_text("\n".join(json.dumps(op) for op in operations))

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = upload_traces("test-project", tmp_path)

        # Should not crash, but should not create any runs
        assert result == {}

    def test_upload_traces_handles_malformed_jsonl(self, mock_client, tmp_path):
        """Verify upload handles malformed JSON gracefully."""
        trace_file = tmp_path / "trace_001.jsonl"
        trace_file.write_text("not valid json\n{also bad")

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            # Should raise or handle gracefully - not silently succeed
            try:
                upload_traces("test-project", tmp_path)
            except json.JSONDecodeError:
                pass  # Expected behavior
            else:
                # If it doesn't raise, verify no runs were created
                assert not mock_client.create_run.called

    def test_cleanup_suffix_matching_is_exact(self, mock_client):
        """Verify cleanup only matches exact suffix, not partial matches in middle."""
        # "bench-run123-extra" contains "-run123" but doesn't END with it
        # Should NOT be deleted when cleaning up run123
        mock_project = MagicMock()
        mock_project.name = "bench-run123-extra"  # Has -run123 in middle, not end

        mock_client.list_projects.return_value = [mock_project]
        mock_client.list_datasets.return_value = []

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = cleanup_namespace("run123")

        # Should NOT delete - suffix is in middle, not at end
        assert mock_client.delete_project.call_count == 0
        assert result["projects"] == []

    def test_dataset_naming_extracts_first_part(self, mock_client, tmp_path):
        """Verify dataset name extracts type from first underscore segment."""
        # sql_agent_trajectory_dataset.json should become bench-sql-{run_id}
        # NOT bench-sql_agent_trajectory-{run_id}
        dataset_file = tmp_path / "mytype_other_parts_dataset.json"
        dataset_file.write_text(json.dumps([{"inputs": {}, "outputs": {}}]))

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            result = upload_datasets(tmp_path, run_id="abc")

        assert "mytype_other_parts_dataset.json" in result
        # Should be bench-mytype-abc (first segment only)
        assert result["mytype_other_parts_dataset.json"] == "bench-mytype-abc"

    def test_id_mapping_preserves_parent_child_relationships(self, mock_client, tmp_path):
        """Verify parent-child relationships are preserved when IDs are remapped."""
        trace_file = tmp_path / "trace_001.jsonl"
        operations = [
            {
                "operation": "post",
                "id": "parent-id",
                "name": "parent",
                "run_type": "chain",
                "inputs": {},
                "start_time": "2024-01-01T00:00:00Z",
            },
            {
                "operation": "post",
                "id": "child-id",
                "name": "child",
                "run_type": "llm",
                "inputs": {},
                "start_time": "2024-01-01T00:00:01Z",
                "parent_run_id": "parent-id",
            },
        ]
        trace_file.write_text("\n".join(json.dumps(op) for op in operations))

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            upload_traces("test-project", tmp_path)

        # Verify child's parent_run_id was remapped (not the old ID)
        calls = mock_client.create_run.call_args_list
        assert len(calls) == 2

        # Find the child call (has parent_run_id)
        child_call = next(c for c in calls if c.kwargs.get("parent_run_id"))
        # Parent ID should have been remapped (not "parent-id")
        assert child_call.kwargs["parent_run_id"] != "parent-id"

    def test_time_shifting_is_consistent(self, mock_client, tmp_path):
        """Verify all timestamps are shifted by the same offset."""
        trace_file = tmp_path / "trace_001.jsonl"
        operations = [
            {
                "operation": "post",
                "id": "run-1",
                "name": "first",
                "run_type": "chain",
                "inputs": {},
                "start_time": "2024-01-01T00:00:00Z",
            },
            {
                "operation": "post",
                "id": "run-2",
                "name": "second",
                "run_type": "chain",
                "inputs": {},
                "start_time": "2024-01-01T00:01:00Z",  # 1 minute later
            },
        ]
        trace_file.write_text("\n".join(json.dumps(op) for op in operations))

        with patch(
            "scaffold.python.external_data_handler._get_langsmith_client",
            return_value=(mock_client, None),
        ):
            upload_traces("test-project", tmp_path)

        # Get the shifted timestamps (they may be datetime objects)
        calls = mock_client.create_run.call_args_list
        times = []
        for c in calls:
            st = c.kwargs["start_time"]
            if isinstance(st, str):
                times.append(_parse_ts(st))
            else:
                times.append(st)

        # The difference between them should still be ~1 minute
        delta = abs((times[1] - times[0]).total_seconds())
        assert 55 < delta < 65  # Allow some tolerance
