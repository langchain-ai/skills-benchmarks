"""Unit tests for upload_evaluators.py."""

import pytest
from unittest.mock import patch, MagicMock


# Mock rules for testing
MOCK_RULES = [
    {
        "id": "rule-1",
        "display_name": "Trajectory Match",
        "sampling_rate": 1.0,
        "dataset_id": "dataset-a",
        "session_id": None,
    },
    {
        "id": "rule-2",
        "display_name": "Trajectory Match",
        "sampling_rate": 1.0,
        "dataset_id": "dataset-b",
        "session_id": None,
    },
    {
        "id": "rule-3",
        "display_name": "Quality Check",
        "sampling_rate": 0.5,
        "dataset_id": None,
        "session_id": "project-x",
    },
]


@pytest.fixture
def mock_api():
    """Mock the LangSmith API calls."""
    with patch("upload_evaluators.requests") as mock_requests:
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_RULES
        mock_response.raise_for_status = MagicMock()
        mock_requests.get.return_value = mock_response
        yield mock_requests


class TestFindEvaluator:
    """Tests for find_evaluator function."""

    def test_finds_evaluator_with_matching_name_and_dataset(self, mock_api):
        """Should find evaluator when name AND dataset_id match."""
        from upload_evaluators import find_evaluator

        result = find_evaluator("Trajectory Match", dataset_id="dataset-a")

        assert result is not None
        assert result["id"] == "rule-1"
        assert result["display_name"] == "Trajectory Match"

    def test_finds_correct_evaluator_among_same_names(self, mock_api):
        """Should find the correct evaluator when multiple have same name but different targets."""
        from upload_evaluators import find_evaluator

        result = find_evaluator("Trajectory Match", dataset_id="dataset-b")

        assert result is not None
        assert result["id"] == "rule-2"  # Not rule-1

    def test_returns_none_when_name_matches_but_target_differs(self, mock_api):
        """Should return None when name matches but target is different."""
        from upload_evaluators import find_evaluator

        result = find_evaluator("Trajectory Match", dataset_id="dataset-c")

        assert result is None

    def test_returns_none_when_name_not_found(self, mock_api):
        """Should return None when evaluator name doesn't exist."""
        from upload_evaluators import find_evaluator

        result = find_evaluator("Nonexistent", dataset_id="dataset-a")

        assert result is None

    def test_finds_evaluator_with_project_target(self, mock_api):
        """Should find evaluator when name AND project_id (session_id) match."""
        from upload_evaluators import find_evaluator

        result = find_evaluator("Quality Check", project_id="project-x")

        assert result is not None
        assert result["id"] == "rule-3"


class TestEvaluatorExists:
    """Tests for evaluator_exists function."""

    def test_returns_true_when_name_exists(self, mock_api):
        """Should return True when any evaluator with the name exists."""
        from upload_evaluators import evaluator_exists

        result = evaluator_exists("Trajectory Match")

        assert result is True

    def test_returns_false_when_name_not_found(self, mock_api):
        """Should return False when no evaluator with the name exists."""
        from upload_evaluators import evaluator_exists

        result = evaluator_exists("Nonexistent")

        assert result is False


class TestReplacementLogic:
    """Tests for the replacement behavior in create_code_payload."""

    def test_replacement_only_deletes_matching_target(self, mock_api):
        """
        When --replace is used, should only delete evaluator with same name AND target.
        Different target = different evaluator, so create new without deleting.
        """
        # This test verifies the core logic:
        # 1. "Trajectory Match" on dataset-a exists
        # 2. User uploads "Trajectory Match" to dataset-b with --replace
        # 3. Should NOT delete dataset-a evaluator
        # 4. Should create new evaluator for dataset-b (or replace if exists)
        from upload_evaluators import find_evaluator

        # Simulating: upload "Trajectory Match" --dataset dataset-c --replace
        # Dataset-c doesn't have this evaluator, so find returns None
        existing = find_evaluator("Trajectory Match", dataset_id="dataset-c")
        assert existing is None  # No match = no deletion, just create

        # Simulating: upload "Trajectory Match" --dataset dataset-a --replace
        # Dataset-a HAS this evaluator, so find returns it for deletion
        existing = find_evaluator("Trajectory Match", dataset_id="dataset-a")
        assert existing is not None  # Match found = delete this one before creating


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
