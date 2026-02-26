"""Test script for ls-multiskill-basic validation.

Checks trajectory dataset structure, accuracy against ground truth, and
LangSmith upload. Runs inside Docker via make_execution_validator.

Usage: python test_dataset.py <dataset_file>
"""

import json
import sys

from scaffold.python.validation.scripts import validate_skill_scripts
from scaffold.python.validation.dataset import (
    validate_dataset_structure,
    validate_dataset_upload,
    validate_trajectory_accuracy,
)


def run_tests(dataset_file):
    passed, failed = [], []

    try:
        outputs = json.loads(open("_outputs.json").read())
    except (FileNotFoundError, json.JSONDecodeError):
        outputs = {}

    # Use current directory as test_dir (Docker mounts test_dir as cwd)
    from pathlib import Path

    test_dir = Path(".")

    # Structure check
    p, f = validate_dataset_structure(
        test_dir, outputs,
        filename=dataset_file,
        min_examples=1,
        dataset_type="trajectory",
    )
    passed.extend(p)
    failed.extend(f)

    # Accuracy check against ground truth (data dir files copied by factory)
    p, f = validate_trajectory_accuracy(
        test_dir, outputs,
        filename=dataset_file,
        expected_filename="expected_dataset.json",
        data_dir=test_dir,
    )
    passed.extend(p)
    failed.extend(f)

    # Upload check
    p, f = validate_dataset_upload(
        test_dir, outputs,
        filename=dataset_file,
        upload_prefix="bench-",
    )
    passed.extend(p)
    failed.extend(f)

    # Script tracking
    events = outputs.get("events", {})
    p, f = validate_skill_scripts(outputs, events)
    passed.extend(p)
    failed.extend(f)

    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    dataset_file = sys.argv[1] if len(sys.argv) > 1 else "trajectory_dataset.json"
    results = run_tests(dataset_file)
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["failed"] else 0)
