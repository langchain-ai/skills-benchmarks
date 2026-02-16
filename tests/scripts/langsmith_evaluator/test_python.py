"""Tests for langsmith-evaluator Python scripts (upload_evaluators.py).

Run with: pytest tests/scripts/langsmith/langsmith-evaluator/test_python.py -v
"""

import pytest

from ..conftest import run_python_script, PY_UPLOAD_EVALUATORS


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
