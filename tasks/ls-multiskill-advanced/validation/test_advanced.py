"""Test script for ls-multiskill-advanced validation.

Checks trajectory dataset structure/accuracy, evaluator existence/syntax/
structure/logic, LangSmith upload, and script usage.
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
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import check_skill_scripts


def _find_evaluator(test_dir):
    path = test_dir / "trajectory_evaluator.py"
    if path.exists():
        return path
    evals = list(test_dir.glob("*evaluator*.py"))
    return evals[0] if evals else None


def check_structure(runner: TestRunner):
    """Dataset has correct structure with trajectory fields."""
    dataset_file = runner.artifacts[0]
    p, f = check_dataset_structure(
        test_dir=Path("."),
        outputs=runner.context,
        filename=dataset_file,
        min_examples=1,
        dataset_type="trajectory",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_evaluator_exists(runner: TestRunner):
    """Check that evaluator file exists."""
    test_dir = Path(".")
    path = test_dir / "trajectory_evaluator.py"
    if path.exists():
        runner.passed("Evaluator: trajectory_evaluator.py exists")
    else:
        evals = list(test_dir.glob("*evaluator*.py"))
        if evals:
            runner.passed(f"Evaluator: {evals[0].name} exists")
        else:
            runner.failed("Evaluator: no evaluator file found")


def check_evaluator_syntax(runner: TestRunner):
    """Check evaluator has valid syntax."""
    test_dir = Path(".")
    path = _find_evaluator(test_dir)
    if not path:
        runner.passed("Evaluator syntax: skipped (no evaluator)")
        return
    try:
        ast.parse(path.read_text())
        runner.passed(f"Evaluator: {path.name} has valid syntax")
    except SyntaxError as e:
        runner.failed(f"Evaluator: {path.name} syntax error: {e.msg}")


def check_evaluator_structure(runner: TestRunner):
    """Check evaluator has correct function structure."""
    test_dir = Path(".")
    path = _find_evaluator(test_dir)
    if not path:
        runner.passed("Evaluator structure: skipped (no evaluator)")
        return
    content = path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if func_name:
        runner.passed(f"Evaluator: has {func_name}(run, example) function")
    elif error:
        runner.failed(f"Evaluator: {error}")
    if "return" in content:
        runner.passed("Evaluator: has return statement")


def check_evaluator_logic(runner: TestRunner):
    """Run evaluator against test cases using eval_runner.py."""
    test_dir = Path(".")
    path = _find_evaluator(test_dir)
    if not path:
        runner.passed("Evaluator logic: skipped (no evaluator)")
        return

    content = path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if error:
        runner.failed(f"Evaluator logic: {error}")
        return

    eval_runner = test_dir / "validation" / "eval_runner.py"
    if not eval_runner.exists():
        runner.passed("Evaluator logic: skipped (no eval_runner.py)")
        return

    test_cases = test_dir / "data" / "evaluator_test_cases.json"
    if not test_cases.exists():
        runner.passed("Evaluator logic: skipped (no test cases)")
        return

    module_name = path.name.replace(".py", "")
    args = [sys.executable, str(eval_runner), module_name, func_name, str(test_cases)]
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
                    for msg in result.get("passed", []):
                        runner.passed(msg)
                    for msg in result.get("failed", []):
                        runner.failed(msg)
                    return
            except json.JSONDecodeError:
                pass
        if r.returncode == 0:
            runner.failed("Evaluator logic: no structured output from eval_runner")
        else:
            runner.failed(f"Evaluator logic: execution failed - {(r.stderr or output)[:100]}")
    except Exception as e:
        runner.failed(f"Evaluator logic: {str(e)[:50]}")


def check_accuracy(runner: TestRunner):
    """Trajectories match ground truth."""
    dataset_file = runner.artifacts[0]
    test_dir = Path(".")
    p, f = check_trajectory_accuracy(
        test_dir=test_dir,
        outputs=runner.context,
        filename=dataset_file,
        expected_filename="expected_dataset.json",
        data_dir=test_dir / "data",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_upload(runner: TestRunner):
    """Check dataset upload to LangSmith."""
    test_dir = Path(".")
    if (test_dir / "trajectory_dataset.json").exists():
        runner.passed("Upload: local dataset file exists")
    if _find_evaluator(test_dir):
        runner.passed("Upload: local evaluator file exists")
    p, f = check_dataset_upload(
        test_dir=test_dir,
        outputs=runner.context,
        filename="trajectory_dataset.json",
        upload_prefix="bench-",
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_scripts(runner: TestRunner):
    """Track which skill scripts Claude used (informational)."""
    p, f = check_skill_scripts(runner.context, runner.context.get("events", {}))
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


if __name__ == "__main__":
    TestRunner.run(
        [
            check_structure,
            check_evaluator_exists,
            check_evaluator_syntax,
            check_evaluator_structure,
            check_evaluator_logic,
            check_accuracy,
            check_upload,
            check_scripts,
        ]
    )
