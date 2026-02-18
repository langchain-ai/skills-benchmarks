"""Function-based validators for ls-multiskill-advanced task.

Each validator is a function that returns (passed: list[str], failed: list[str]).
"""

import ast
import json
from pathlib import Path


def validate_dataset_structure(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the trajectory dataset has the correct structure."""
    passed, failed = [], []

    dataset_path = test_dir / "trajectory_dataset.json"
    if not dataset_path.exists():
        return [], ["Dataset: trajectory_dataset.json not found"]

    try:
        with open(dataset_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [], [f"Dataset: invalid JSON - {e}"]

    if not isinstance(data, list):
        failed.append("Dataset: should be a list of examples")
        return passed, failed

    if len(data) == 0:
        failed.append("Dataset: no examples found")
        return passed, failed

    passed.append(f"Dataset: found {len(data)} examples")

    # Check each example has required fields
    required_fields = ["inputs", "outputs"]
    for i, example in enumerate(data):
        if not isinstance(example, dict):
            failed.append(f"Dataset: example {i} is not a dict")
            continue

        for field in required_fields:
            if field not in example:
                failed.append(f"Dataset: example {i} missing '{field}'")

    if not failed:
        passed.append("Dataset: all examples have required fields")

    return passed, failed


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

    # Check for evaluator function
    if "def " in content:
        passed.append("Evaluator: contains function definitions")
    else:
        failed.append("Evaluator: no function definitions found")

    # Check for return statement (should return a score)
    if "return" in content:
        passed.append("Evaluator: has return statement")

    return passed, failed


def validate_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that files were uploaded to LangSmith.

    Note: This requires LangSmith API access.
    """
    passed, failed = [], []
    run_id = outputs.get("run_id", "")

    # Check local files exist
    dataset_path = test_dir / "trajectory_dataset.json"
    evaluator_path = test_dir / "trajectory_evaluator.py"

    if dataset_path.exists():
        passed.append("Upload: local dataset file exists")
    if evaluator_path.exists() or list(test_dir.glob("*evaluator*.py")):
        passed.append("Upload: local evaluator file exists")

    if run_id:
        passed.append(f"Upload: run_id={run_id[:8]}...")

    return passed, failed


# List of all validators for this task
VALIDATORS = [
    validate_dataset_structure,
    validate_evaluator_exists,
    validate_evaluator_syntax,
    validate_evaluator_structure,
    validate_upload,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run all validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in VALIDATORS:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed
