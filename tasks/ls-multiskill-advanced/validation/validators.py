"""Function-based validators for ls-multiskill-advanced task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates both a trajectory dataset and
a Python evaluator from LangSmith traces.
"""

import ast
from pathlib import Path

from scaffold.python.utils import run_python_in_docker
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


def validate_evaluator_logic(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run evaluator on test cases to verify it works correctly."""
    import json

    passed, failed = [], []

    # Find evaluator file
    evaluator_path = test_dir / "trajectory_evaluator.py"
    if not evaluator_path.exists():
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            evaluator_path = evals[0]
        else:
            return [], []  # No evaluator to test

    # Find evaluator function
    content = evaluator_path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if error:
        return [], [f"Evaluator logic: {error}"]

    # Copy eval_runner.py to test directory
    validation_dir = Path(__file__).parent
    runner_src = validation_dir / "eval_runner.py"
    runner_dst = test_dir / "_eval_runner.py"
    if not runner_src.exists():
        return ["Evaluator logic: skipped (no eval_runner.py)"], []

    runner_dst.write_text(runner_src.read_text())

    # Use ground truth test cases
    dataset_path = test_dir / "trajectory_dataset.json"
    test_cases_path = validation_dir.parent / "data" / "evaluator_test_cases.json"

    try:
        module_name = evaluator_path.name.replace(".py", "")
        args = [module_name, func_name, "evaluator_test_cases.json"]

        # Copy test cases
        if test_cases_path.exists():
            (test_dir / "evaluator_test_cases.json").write_text(test_cases_path.read_text())
        else:
            return ["Evaluator logic: skipped (no test cases)"], []

        # Add dataset path for dynamic test generation
        if dataset_path.exists():
            args.append("trajectory_dataset.json")

        success, output = run_python_in_docker(test_dir, "_eval_runner.py", timeout=60, args=args)

        # Parse results
        for line in output.split("\n"):
            if line.startswith("EVALUATOR_RESULTS:"):
                try:
                    results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                    passed_count = sum(1 for r in results if r.get("passed"))
                    total = len(results)
                    msg = f"Evaluator logic: {passed_count}/{total} tests"
                    if passed_count == total:
                        passed.append(msg + " passed")
                    elif passed_count > total // 2:
                        passed.append(msg + " (partial)")
                    else:
                        failed.append(msg + " passed")
                    return passed, failed
                except json.JSONDecodeError:
                    pass

        if success:
            passed.append("Evaluator logic: executed")
        else:
            failed.append(f"Evaluator logic: execution failed - {output[:100]}")

    except Exception as e:
        failed.append(f"Evaluator logic: {str(e)[:50]}")
    finally:
        runner_dst.unlink(missing_ok=True)
        (test_dir / "evaluator_test_cases.json").unlink(missing_ok=True)

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
    validate_evaluator_logic,
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
