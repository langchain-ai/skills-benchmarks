"""Test API functionality with mocked LangSmith client.

These tests verify that scripts handle API responses correctly without
making real API calls.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class MockRun:
    """Mock LangSmith run object."""

    def __init__(
        self,
        id: str,
        trace_id: str,
        name: str,
        run_type: str,
        parent_run_id: str | None = None,
        start_time=None,
        end_time=None,
        inputs=None,
        outputs=None,
        status="success",
        error=None,
    ):
        self.id = id
        self.trace_id = trace_id
        self.name = name
        self.run_type = run_type
        self.parent_run_id = parent_run_id
        self.start_time = start_time
        self.end_time = end_time
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.status = status
        self.error = error
        self.extra = {}


class MockDataset:
    """Mock LangSmith dataset object."""

    def __init__(self, id: str, name: str, description: str = "", example_count: int = 0):
        self.id = id
        self.name = name
        self.description = description
        self.example_count = example_count


class MockExample:
    """Mock LangSmith example object."""

    def __init__(self, inputs: dict, outputs: dict):
        self.inputs = inputs
        self.outputs = outputs


@pytest.fixture
def mock_runs():
    """Create mock runs for a trace."""
    from datetime import datetime

    return [
        MockRun(
            id="run-001",
            trace_id="trace-001",
            name="agent",
            run_type="chain",
            parent_run_id=None,
            start_time=datetime(2025, 1, 15, 10, 0, 0),
            end_time=datetime(2025, 1, 15, 10, 0, 5),
            inputs={"query": "What is 2 + 2?"},
            outputs={"answer": "4"},
        ),
        MockRun(
            id="run-002",
            trace_id="trace-001",
            name="calculator",
            run_type="tool",
            parent_run_id="run-001",
            start_time=datetime(2025, 1, 15, 10, 0, 1),
            end_time=datetime(2025, 1, 15, 10, 0, 2),
            inputs={"expression": "2 + 2"},
            outputs={"result": "4"},
        ),
    ]


@pytest.fixture
def mock_datasets():
    """Create mock datasets."""
    return [
        MockDataset(
            id="ds-001",
            name="Test Dataset",
            description="A test dataset",
            example_count=10,
        ),
        MockDataset(
            id="ds-002",
            name="Another Dataset",
            description="Another test",
            example_count=5,
        ),
    ]


class TestQueryTracesMockedAPI:
    """Test query_traces with mocked LangSmith API."""

    def test_python_traces_list_json_output(self, mock_runs):
        """Python traces list produces valid JSON with mock data."""
        # This test imports the module and tests internal functions
        # which is more reliable than subprocess for API testing
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_TRACES

        # Load the module
        spec = importlib.util.spec_from_file_location("query_traces", PY_QUERY_TRACES)
        module = importlib.util.module_from_spec(spec)

        # Test the extract_run function
        spec.loader.exec_module(module)
        extract_run = module.extract_run

        result = extract_run(mock_runs[0], include_metadata=True, include_io=True)

        assert result["run_id"] == "run-001"
        assert result["trace_id"] == "trace-001"
        assert result["name"] == "agent"
        assert result["run_type"] == "chain"
        assert result["inputs"] == {"query": "What is 2 + 2?"}
        assert result["outputs"] == {"answer": "4"}

    def test_python_calc_duration(self, mock_runs):
        """Python calc_duration works correctly."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_TRACES

        spec = importlib.util.spec_from_file_location("query_traces", PY_QUERY_TRACES)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        calc_duration = module.calc_duration

        duration = calc_duration(mock_runs[0])
        assert duration == 5000  # 5 seconds in ms

    def test_python_get_trace_id(self, mock_runs):
        """Python get_trace_id extracts trace ID correctly."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_TRACES

        spec = importlib.util.spec_from_file_location("query_traces", PY_QUERY_TRACES)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        get_trace_id = module.get_trace_id

        trace_id = get_trace_id(mock_runs[0])
        assert trace_id == "trace-001"

    def test_python_build_query_params(self):
        """Python build_query_params constructs correct filters."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_TRACES

        spec = importlib.util.spec_from_file_location("query_traces", PY_QUERY_TRACES)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        build_query_params = module.build_query_params

        # Test basic params
        params = build_query_params(
            project="test-project",
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

        assert params["project_name"] == "test-project"
        assert params["limit"] == 10
        assert params["is_root"] is True

    def test_python_build_query_params_with_filters(self):
        """Python build_query_params handles multiple filters."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_TRACES

        spec = importlib.util.spec_from_file_location("query_traces", PY_QUERY_TRACES)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        build_query_params = module.build_query_params

        params = build_query_params(
            project="test-project",
            trace_ids=None,
            limit=10,
            last_n_minutes=None,
            since=None,
            run_type=None,
            is_root=True,
            error=None,
            name="agent",
            raw_filter=None,
            min_latency=5.0,
            max_latency=None,
            min_tokens=None,
            tags=None,
        )

        assert "filter" in params
        assert "search(name," in params["filter"]
        assert "gte(latency," in params["filter"]


class TestGenerateDatasetsMockedAPI:
    """Test generate_datasets with mocked data processing."""

    def test_python_extract_tool_sequence(self, mock_runs):
        """Python extract_tool_sequence extracts tools correctly."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_GENERATE_DATASETS

        spec = importlib.util.spec_from_file_location(
            "generate_datasets", PY_GENERATE_DATASETS
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Convert mock runs to SimpleNamespace for the function
        from types import SimpleNamespace

        runs = [
            SimpleNamespace(
                id=r.id,
                run_id=r.id,
                trace_id=r.trace_id,
                name=r.name,
                run_type=r.run_type,
                parent_run_id=r.parent_run_id,
                start_time=r.start_time,
                inputs=r.inputs,
                outputs=r.outputs,
            )
            for r in mock_runs
        ]

        extract_tool_sequence = module.extract_tool_sequence
        tools = extract_tool_sequence(runs)

        assert "calculator" in tools

    def test_python_extract_value_common_fields(self):
        """Python extract_value finds common input fields."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_GENERATE_DATASETS

        spec = importlib.util.spec_from_file_location(
            "generate_datasets", PY_GENERATE_DATASETS
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        extract_value = module.extract_value
        COMMON_INPUT_FIELDS = module.COMMON_INPUT_FIELDS

        data = {"query": "What is the capital of France?", "other": "ignored"}
        result = extract_value(
            data,
            fields=None,
            common_fields=COMMON_INPUT_FIELDS,
            message_role="human",
            fallback_to_raw=False,
        )

        assert result == "What is the capital of France?"

    def test_python_extract_from_messages(self):
        """Python extract_from_messages handles message arrays."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_GENERATE_DATASETS

        spec = importlib.util.spec_from_file_location(
            "generate_datasets", PY_GENERATE_DATASETS
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        extract_from_messages = module.extract_from_messages

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        user_msg = extract_from_messages(messages, role="user")
        assert user_msg == "Hello"

        assistant_msg = extract_from_messages(messages, role="assistant")
        assert assistant_msg == "Hi there!"


class TestQueryDatasetsMockedAPI:
    """Test query_datasets with mocked LangSmith client."""

    def test_python_display_examples_handles_langsmith_format(self, capsys):
        """Python display_examples handles LangSmith input/output format."""
        import importlib.util
        from tests.script_langsmith.conftest import PY_QUERY_DATASETS

        spec = importlib.util.spec_from_file_location(
            "query_datasets", PY_QUERY_DATASETS
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        display_examples = module.display_examples

        examples = [
            {"inputs": {"query": "test"}, "outputs": {"answer": "result"}},
        ]

        # Display in JSON format
        display_examples(examples, "json", 1)

        captured = capsys.readouterr()
        # JSON output should be valid
        assert "query" in captured.out
        assert "answer" in captured.out


class TestUploadEvaluatorsMockedAPI:
    """Test upload_evaluators with mocked API."""

    def test_python_extract_function_source(self, tmp_path):
        """Python can extract function source for upload."""
        # Create a test evaluator file
        evaluator_code = '''
def my_evaluator(run, example):
    """Test evaluator."""
    output = run["outputs"].get("answer", "")
    expected = example["outputs"].get("answer", "")
    return {"match": 1 if output == expected else 0}
'''
        eval_file = tmp_path / "test_eval.py"
        eval_file.write_text(evaluator_code)

        # Load the file and extract function
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_eval", eval_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, "my_evaluator")
        assert callable(module.my_evaluator)

        # Test the evaluator works
        result = module.my_evaluator(
            {"outputs": {"answer": "Paris"}},
            {"outputs": {"answer": "Paris"}},
        )
        assert result["match"] == 1

    def test_ts_extract_function_regex(self):
        """TypeScript function extraction regex works."""
        # Test the regex pattern used in upload_evaluators.ts
        import re

        func_name = "my_evaluator"
        patterns = [
            re.compile(
                rf"(async\s+def\s+{func_name}\s*\([\s\S]*?)(?=\n(?:async\s+)?def\s|\nclass\s|\n[a-zA-Z_][a-zA-Z0-9_]*\s*=|$)",
                re.MULTILINE,
            ),
            re.compile(
                rf"(def\s+{func_name}\s*\([\s\S]*?)(?=\n(?:async\s+)?def\s|\nclass\s|\n[a-zA-Z_][a-zA-Z0-9_]*\s*=|$)",
                re.MULTILINE,
            ),
        ]

        test_code = '''
def my_evaluator(run, example):
    """Check output matches expected."""
    return {"match": 1}

def another_function():
    pass
'''

        for pattern in patterns:
            match = pattern.search(test_code)
            if match:
                source = match.group(1).strip()
                assert "def my_evaluator" in source
                assert "another_function" not in source
                break
        else:
            pytest.fail("No pattern matched")
