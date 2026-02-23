"""Function-based validators for ls-multiskill-advanced task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates both a trajectory dataset and
a Python evaluator from LangSmith traces.
"""

import ast
from pathlib import Path

from scaffold.python.validation import (
    find_evaluator_function,
    validate_dataset_structure,
    validate_dataset_upload,
    validate_skill_scripts,
    validate_trajectory_accuracy,
)


def validate_dataset_structure_fn(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the trajectory dataset has the correct structure."""
    return validate_dataset_structure(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        min_examples=1,
        dataset_type="trajectory",
    )


def validate_evaluator_exists(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that an evaluator file was created."""
    passed, failed = [], []

    evaluator_path = test_dir / "trajectory_evaluator.py"
    if evaluator_path.exists():
        passed.append("Evaluator: trajectory_evaluator.py exists")
    else:
        # Check for any evaluator file
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            passed.append(f"Evaluator: {evals[0].name} exists")
        else:
            failed.append("Evaluator: no evaluator file found")

    return passed, failed


def validate_evaluator_syntax(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the evaluator has valid Python syntax."""
    passed, failed = [], []

    evaluator_path = test_dir / "trajectory_evaluator.py"
    if not evaluator_path.exists():
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            evaluator_path = evals[0]
        else:
            return [], []

    content = evaluator_path.read_text()
    try:
        ast.parse(content)
        passed.append(f"Evaluator: {evaluator_path.name} has valid syntax")
    except SyntaxError as e:
        failed.append(f"Evaluator: {evaluator_path.name} syntax error: {e.msg}")

    return passed, failed


def validate_evaluator_structure(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the evaluator has the expected structure."""
    passed, failed = [], []

    evaluator_path = test_dir / "trajectory_evaluator.py"
    if not evaluator_path.exists():
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            evaluator_path = evals[0]
        else:
            return [], []

    content = evaluator_path.read_text()

    # Find evaluator function
    func_name, error = find_evaluator_function(content, "python")
    if func_name:
        passed.append(f"Evaluator: has {func_name}(run, example) function")
    elif error:
        failed.append(f"Evaluator: {error}")

    # Check for return statement (should return a score)
    if "return" in content:
        passed.append("Evaluator: has return statement")

    return passed, failed


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
    """Validate that files were uploaded to LangSmith."""
    passed, failed = [], []

    # Check local files exist
    dataset_path = test_dir / "trajectory_dataset.json"
    evaluator_path = test_dir / "trajectory_evaluator.py"

    if dataset_path.exists():
        passed.append("Upload: local dataset file exists")
    if evaluator_path.exists() or list(test_dir.glob("*evaluator*.py")):
        passed.append("Upload: local evaluator file exists")

    # Check LangSmith upload
    ds_passed, ds_failed = validate_dataset_upload(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        upload_prefix="bench-",
    )
    passed.extend(ds_passed)
    failed.extend(ds_failed)

    return passed, failed


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# List of all validators for this task
VALIDATORS = [
    validate_dataset_structure_fn,
    validate_evaluator_exists,
    validate_evaluator_syntax,
    validate_evaluator_structure,
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
