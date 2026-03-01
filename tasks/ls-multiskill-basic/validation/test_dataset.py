"""Test script for ls-multiskill-basic validation.

Checks trajectory dataset structure, accuracy against ground truth, and
LangSmith upload. Runs inside Docker via make_execution_validator.
"""

from scaffold.python.validation.dataset import (
    check_dataset_structure,
    check_dataset_upload,
    check_trajectory_accuracy,
)
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import check_skill_scripts


def check_structure(runner: TestRunner):
    """Dataset has correct structure with trajectory fields."""
    dataset_file = runner.artifacts[0]
    p, f = check_dataset_structure(
        outputs=runner.context,
        filename=dataset_file,
        min_examples=1,
        dataset_type="trajectory",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_accuracy(runner: TestRunner):
    """Trajectories match ground truth."""
    dataset_file = runner.artifacts[0]
    p, f = check_trajectory_accuracy(
        outputs=runner.context,
        filename=dataset_file,
        expected_filename="expected_dataset.json",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_upload(runner: TestRunner):
    """Dataset uploaded to LangSmith."""
    dataset_file = runner.artifacts[0]
    p, f = check_dataset_upload(
        outputs=runner.context,
        filename=dataset_file,
        upload_prefix="bench-",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_scripts(runner: TestRunner):
    """Track which skill scripts Claude used (informational)."""
    events = runner.context.get("events", {})
    p, f = check_skill_scripts(runner.context, events)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


if __name__ == "__main__":
    TestRunner.run([check_structure, check_accuracy, check_upload, check_scripts])
