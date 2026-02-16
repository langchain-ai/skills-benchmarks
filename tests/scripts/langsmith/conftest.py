"""Shared fixtures for LangSmith script tests."""

from pathlib import Path

import pytest

# Re-export shared utilities
from tests.scripts.conftest import run_python_script, run_ts_script

# Script paths - relative to skills/benchmarks
SCRIPTS_BASE = Path(__file__).parent.parent.parent.parent / "skills" / "benchmarks"

PY_QUERY_TRACES = SCRIPTS_BASE / "langsmith_trace-py" / "scripts" / "query_traces.py"
TS_QUERY_TRACES = SCRIPTS_BASE / "langsmith_trace-js" / "scripts" / "query_traces.ts"

PY_GENERATE_DATASETS = (
    SCRIPTS_BASE / "langsmith_dataset-py" / "scripts" / "generate_datasets.py"
)
TS_GENERATE_DATASETS = (
    SCRIPTS_BASE / "langsmith_dataset-js" / "scripts" / "generate_datasets.ts"
)

PY_QUERY_DATASETS = SCRIPTS_BASE / "langsmith_dataset-py" / "scripts" / "query_datasets.py"
TS_QUERY_DATASETS = SCRIPTS_BASE / "langsmith_dataset-js" / "scripts" / "query_datasets.ts"

PY_UPLOAD_EVALUATORS = (
    SCRIPTS_BASE / "langsmith_evaluator-py" / "scripts" / "upload_evaluators.py"
)
TS_UPLOAD_EVALUATORS = (
    SCRIPTS_BASE / "langsmith_evaluator-js" / "scripts" / "upload_evaluators.ts"
)


@pytest.fixture
def py_query_traces():
    """Python query_traces.py script path."""
    return PY_QUERY_TRACES


@pytest.fixture
def ts_query_traces():
    """TypeScript query_traces.ts script path."""
    return TS_QUERY_TRACES


@pytest.fixture
def py_generate_datasets():
    """Python generate_datasets.py script path."""
    return PY_GENERATE_DATASETS


@pytest.fixture
def ts_generate_datasets():
    """TypeScript generate_datasets.ts script path."""
    return TS_GENERATE_DATASETS


@pytest.fixture
def py_query_datasets():
    """Python query_datasets.py script path."""
    return PY_QUERY_DATASETS


@pytest.fixture
def ts_query_datasets():
    """TypeScript query_datasets.ts script path."""
    return TS_QUERY_DATASETS


@pytest.fixture
def py_upload_evaluators():
    """Python upload_evaluators.py script path."""
    return PY_UPLOAD_EVALUATORS


@pytest.fixture
def ts_upload_evaluators():
    """TypeScript upload_evaluators.ts script path."""
    return TS_UPLOAD_EVALUATORS
