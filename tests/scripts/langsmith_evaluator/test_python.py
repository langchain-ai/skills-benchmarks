"""Tests for langsmith-evaluator Python scripts (upload_evaluators.py).

Run with: pytest tests/scripts/langsmith_evaluator/test_python.py -v
"""

import os
import sys
from unittest.mock import patch

import pytest
import responses

from ..conftest import (
    PY_UPLOAD_EVALUATORS,
    SAMPLE_EVALUATORS,
    SCRIPTS_BASE,
    run_python_script,
)


@pytest.fixture
def script_path():
    """Path to upload_evaluators.py."""
    return PY_UPLOAD_EVALUATORS


class TestCLIHelp:
    """Test CLI help output."""

    def test_main_help(self, script_path):
        """Provides main help output."""
        result = run_python_script(script_path, ["--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "list" in result.stdout.lower()
        assert "upload" in result.stdout.lower()
        assert "delete" in result.stdout.lower()

    def test_upload_help(self, script_path):
        """upload subcommand help."""
        result = run_python_script(script_path, ["upload", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert "--name" in result.stdout
        assert "--function" in result.stdout

    def test_list_help(self, script_path):
        """list subcommand help."""
        result = run_python_script(script_path, ["list", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"

    def test_delete_help(self, script_path):
        """delete subcommand help."""
        result = run_python_script(script_path, ["delete", "--help"])
        assert result.returncode == 0, f"Failed: {result.stderr}"


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
            "LANGSMITH_API_URL": "https://api.smith.langchain.com",
        },
    ):
        yield


@pytest.fixture
def upload_module(mock_env):
    """Import the upload_evaluators module with mocked env."""
    # Add script directory to path
    script_dir = SCRIPTS_BASE / "langsmith_evaluator" / "scripts"
    sys.path.insert(0, str(script_dir))

    # Clear any cached imports
    if "upload_evaluators" in sys.modules:
        del sys.modules["upload_evaluators"]

    try:
        import upload_evaluators

        yield upload_evaluators
    finally:
        sys.path.remove(str(script_dir))
        if "upload_evaluators" in sys.modules:
            del sys.modules["upload_evaluators"]


class TestMockedAPIFunctions:
    """Test API functions with mocked HTTP responses."""

    @responses.activate
    def test_evaluator_exists_true(self, upload_module):
        """evaluator_exists returns True when evaluator is found."""
        responses.add(
            responses.GET,
            "https://api.smith.langchain.com/runs/rules",
            json=SAMPLE_EVALUATORS,
            status=200,
        )

        result = upload_module.evaluator_exists("response_quality")
        assert result is True

    @responses.activate
    def test_evaluator_exists_false(self, upload_module):
        """evaluator_exists returns False when evaluator not found."""
        responses.add(
            responses.GET,
            "https://api.smith.langchain.com/runs/rules",
            json=SAMPLE_EVALUATORS,
            status=200,
        )

        result = upload_module.evaluator_exists("nonexistent_evaluator")
        assert result is False

    @responses.activate
    def test_evaluator_exists_empty_list(self, upload_module):
        """evaluator_exists returns False for empty list."""
        responses.add(
            responses.GET,
            "https://api.smith.langchain.com/runs/rules",
            json=[],
            status=200,
        )

        result = upload_module.evaluator_exists("any_name")
        assert result is False

    @responses.activate
    def test_get_headers(self, upload_module):
        """get_headers returns correct authentication headers."""
        headers = upload_module.get_headers()

        assert "x-api-key" in headers
        assert headers["x-api-key"] == "test-api-key-12345"
        assert headers["Content-Type"] == "application/json"

    @responses.activate
    def test_delete_evaluator_not_found(self, upload_module):
        """delete_evaluator handles non-existent evaluator."""
        responses.add(
            responses.GET,
            "https://api.smith.langchain.com/runs/rules",
            json=[],
            status=200,
        )

        result = upload_module.delete_evaluator("nonexistent", confirm=False)
        assert result is False

    @responses.activate
    def test_delete_evaluator_success(self, upload_module):
        """delete_evaluator successfully deletes evaluator."""
        # Mock GET to find the evaluator
        responses.add(
            responses.GET,
            "https://api.smith.langchain.com/runs/rules",
            json=SAMPLE_EVALUATORS,
            status=200,
        )

        # Mock DELETE to remove it
        eval_id = SAMPLE_EVALUATORS[0]["id"]
        responses.add(
            responses.DELETE,
            f"https://api.smith.langchain.com/runs/rules/{eval_id}",
            status=200,
        )

        result = upload_module.delete_evaluator("response_quality", confirm=False)
        assert result is True

    @responses.activate
    def test_create_evaluator_success(self, upload_module):
        """create_evaluator successfully uploads evaluator."""
        responses.add(
            responses.POST,
            "https://api.smith.langchain.com/runs/rules",
            status=200,
        )

        payload = upload_module.EvaluatorPayload(
            display_name="test_evaluator",
            evaluators=[
                upload_module.CodeEvaluator(
                    code="def perform_eval(inputs, outputs, reference_outputs):\n    return {'score': 1.0}",
                    language="python",
                )
            ],
            sampling_rate=1.0,
            target_dataset_ids=["test-dataset-id"],
        )

        result = upload_module.create_evaluator(payload)
        assert result is True

    @responses.activate
    def test_create_evaluator_failure(self, upload_module):
        """create_evaluator handles upload failure."""
        responses.add(
            responses.POST,
            "https://api.smith.langchain.com/runs/rules",
            json={"error": "Invalid payload"},
            status=400,
        )

        payload = upload_module.EvaluatorPayload(
            display_name="test_evaluator",
            evaluators=[
                upload_module.CodeEvaluator(
                    code="invalid code",
                    language="python",
                )
            ],
            sampling_rate=1.0,
            target_dataset_ids=["test-dataset-id"],
        )

        result = upload_module.create_evaluator(payload)
        assert result is False
