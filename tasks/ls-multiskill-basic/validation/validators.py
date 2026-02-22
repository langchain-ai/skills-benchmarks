"""Function-based validators for ls-multiskill-basic task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates a trajectory dataset from LangSmith traces.
"""

from pathlib import Path

from scaffold.python.validation import (
    validate_dataset_structure,
    validate_dataset_upload,
    validate_skill_scripts,
    validate_trajectory_accuracy,
)


def validate_structure(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the trajectory dataset has the correct structure."""
    return validate_dataset_structure(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        min_examples=1,
        dataset_type="trajectory",
    )


def validate_accuracy(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the trajectory dataset matches expected format."""
    data_dir = Path(__file__).parent.parent / "data"
    return validate_trajectory_accuracy(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        expected_filename="expected_dataset.json",
        data_dir=data_dir,
    )


def validate_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the dataset was uploaded to LangSmith."""
    return validate_dataset_upload(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        upload_prefix="bench-",
    )


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# List of all validators for this task
VALIDATORS = [
    validate_structure,
    validate_accuracy,
    validate_upload,
    validate_scripts,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run all validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in VALIDATORS:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed
