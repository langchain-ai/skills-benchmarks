"""Test script for ls-multiskill-advanced validation.

Checks trajectory dataset structure/accuracy, evaluator existence/syntax/
structure/logic, LangSmith upload, and script usage.
Runs inside Docker via make_execution_validator.

Usage: python test_advanced.py <dataset_file>
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

from scaffold.python.validation.dataset import (
    check_dataset_structure,
    check_dataset_upload,
    check_trajectory_accuracy,
)
from scaffold.python.validation.evaluator import find_evaluator_function
from scaffold.python.validation.scripts import check_skill_scripts


def check_evaluator_exists(test_dir):
    passed, failed = [], []
    path = test_dir / "trajectory_evaluator.py"
    if path.exists():
        passed.append("Evaluator: trajectory_evaluator.py exists")
    else:
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            passed.append(f"Evaluator: {evals[0].name} exists")
        else:
            failed.append("Evaluator: no evaluator file found")
    return passed, failed


def _find_evaluator(test_dir):
    path = test_dir / "trajectory_evaluator.py"
    if path.exists():
        return path
    evals = list(test_dir.glob("*evaluator*.py"))
    return evals[0] if evals else None


def check_evaluator_syntax(test_dir):
    passed, failed = [], []
    path = _find_evaluator(test_dir)
    if not path:
        return [], []
    try:
        ast.parse(path.read_text())
        passed.append(f"Evaluator: {path.name} has valid syntax")
    except SyntaxError as e:
        failed.append(f"Evaluator: {path.name} syntax error: {e.msg}")
    return passed, failed


def check_evaluator_structure(test_dir):
    passed, failed = [], []
    path = _find_evaluator(test_dir)
    if not path:
        return [], []
    content = path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if func_name:
        passed.append(f"Evaluator: has {func_name}(run, example) function")
    elif error:
        failed.append(f"Evaluator: {error}")
    if "return" in content:
        passed.append("Evaluator: has return statement")
    return passed, failed


def check_evaluator_logic(test_dir):
    """Run evaluator against test cases using eval_runner.py."""
    path = _find_evaluator(test_dir)
    if not path:
        return [], []

    content = path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if error:
        return [], [f"Evaluator logic: {error}"]

    runner = test_dir / "eval_runner.py"
    if not runner.exists():
        return ["Evaluator logic: skipped (no eval_runner.py)"], []

    test_cases = test_dir / "evaluator_test_cases.json"
    if not test_cases.exists():
        return ["Evaluator logic: skipped (no test cases)"], []

    module_name = path.name.replace(".py", "")
    args = [sys.executable, str(runner), module_name, func_name, "evaluator_test_cases.json"]
    if (test_dir / "trajectory_dataset.json").exists():
        args.append("trajectory_dataset.json")

    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=str(test_dir))
        output = r.stdout.strip()
        # eval_runner.py outputs standard JSON: {"passed": [...], "failed": [...]}
        if output:
            try:
                result = json.loads(output)
                if isinstance(result, dict):
                    return result.get("passed", []), result.get("failed", [])
            except json.JSONDecodeError:
                pass
        if r.returncode == 0:
            return [], ["Evaluator logic: no structured output from eval_runner"]
        return [], [f"Evaluator logic: execution failed - {(r.stderr or output)[:100]}"]
    except Exception as e:
        return [], [f"Evaluator logic: {str(e)[:50]}"]


def check_upload(test_dir, outputs):
    passed, failed = [], []
    if (test_dir / "trajectory_dataset.json").exists():
        passed.append("Upload: local dataset file exists")
    if _find_evaluator(test_dir):
        passed.append("Upload: local evaluator file exists")
    p, f = check_dataset_upload(
        test_dir,
        outputs,
        filename="trajectory_dataset.json",
        upload_prefix="bench-",
    )
    passed.extend(p)
    failed.extend(f)
    return passed, failed


def run_tests(dataset_file):
    passed, failed = [], []
    test_dir = Path(".")

    try:
        outputs = json.loads(open("_outputs.json").read())
    except (FileNotFoundError, json.JSONDecodeError):
        outputs = {}

    for p, f in [
        check_dataset_structure(
            test_dir,
            outputs,
            filename=dataset_file,
            min_examples=1,
            dataset_type="trajectory",
        ),
        check_evaluator_exists(test_dir),
        check_evaluator_syntax(test_dir),
        check_evaluator_structure(test_dir),
        check_evaluator_logic(test_dir),
        check_trajectory_accuracy(
            test_dir,
            outputs,
            filename=dataset_file,
            expected_filename="expected_dataset.json",
            data_dir=test_dir,
        ),
        check_upload(test_dir, outputs),
        check_skill_scripts(outputs, outputs.get("events", {})),
    ]:
        passed.extend(p)
        failed.extend(f)

    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    dataset_file = sys.argv[1] if len(sys.argv) > 1 else "trajectory_dataset.json"
    results = run_tests(dataset_file)
    print(json.dumps(results, indent=2))
    with open("_test_results.json", "w") as f:
        json.dump(results, f)
    sys.exit(1 if results["failed"] else 0)
