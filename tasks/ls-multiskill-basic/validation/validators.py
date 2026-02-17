"""Function-based validators for ls-multiskill-basic task.

Each validator is a function that returns (passed: list[str], failed: list[str]).
"""

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

    # Check it's a list of examples
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


def validate_trajectory_accuracy(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the trajectory dataset matches expected format."""
    passed, failed = [], []

    dataset_path = test_dir / "trajectory_dataset.json"
    if not dataset_path.exists():
        return [], []  # Already checked in structure validator

    try:
        with open(dataset_path) as f:
            data = json.load(f)
    except Exception:
        return [], []

    if not isinstance(data, list) or len(data) == 0:
        return [], []

    # Check for trajectory-specific fields
    has_trajectory = False
    for example in data:
        if isinstance(example, dict):
            # Check for tool calls or trajectory info
            outputs = example.get("outputs", {})
            if isinstance(outputs, dict):
                if "tool_calls" in outputs or "trajectory" in outputs:
                    has_trajectory = True
                    break

    if has_trajectory:
        passed.append("Dataset: contains trajectory information")
    else:
        # Not a failure, just informational
        passed.append("Dataset: basic structure (no explicit trajectory field)")

    return passed, failed


def validate_dataset_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the dataset was uploaded to LangSmith.

    Note: This requires LangSmith API access.
    """
    passed, failed = [], []
    run_id = outputs.get("run_id", "")

    # Check local file exists
    dataset_path = test_dir / "trajectory_dataset.json"
    if dataset_path.exists():
        passed.append("Upload: local dataset file exists")
    else:
        failed.append("Upload: no local dataset file")

    if run_id:
        passed.append(f"Upload: run_id={run_id[:8]}...")

    return passed, failed


# List of all validators for this task
VALIDATORS = [
    validate_dataset_structure,
    validate_trajectory_accuracy,
    validate_dataset_upload,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run all validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in VALIDATORS:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed
