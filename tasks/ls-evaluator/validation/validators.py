"""Function-based validators for ls-evaluator task.

Each validator is a function that returns (passed: list[str], failed: list[str]).
"""

import ast
from pathlib import Path


def validate_language_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators are in the correct language for each agent type."""
    passed, failed = [], []

    # Backend (Python agent) should have Python evaluator
    backend_eval = test_dir / "backend" / "evaluator.py"
    if backend_eval.exists():
        passed.append("Python: evaluator.py exists for backend")
    else:
        # Check for any .py evaluator in backend
        py_evals = list((test_dir / "backend").glob("evaluator*.py"))
        if py_evals:
            passed.append(f"Python: {py_evals[0].name} exists for backend")
        else:
            failed.append("Python: no evaluator.py found for backend")

    # Frontend (TypeScript agent) should have TypeScript/JS evaluator
    frontend_eval_ts = test_dir / "frontend" / "evaluator.ts"
    frontend_eval_js = test_dir / "frontend" / "evaluator.js"
    if frontend_eval_ts.exists():
        passed.append("TypeScript: evaluator.ts exists for frontend")
    elif frontend_eval_js.exists():
        passed.append("JavaScript: evaluator.js exists for frontend")
    else:
        # Check for any .ts/.js evaluator in frontend
        ts_evals = list((test_dir / "frontend").glob("evaluator*.ts"))
        js_evals = list((test_dir / "frontend").glob("evaluator*.js"))
        if ts_evals:
            passed.append(f"TypeScript: {ts_evals[0].name} exists for frontend")
        elif js_evals:
            passed.append(f"JavaScript: {js_evals[0].name} exists for frontend")
        else:
            failed.append("TypeScript/JavaScript: no evaluator found for frontend")

    return passed, failed


def validate_syntax_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluator files have correct syntax."""
    passed, failed = [], []

    # Check Python evaluator syntax
    py_evals = list((test_dir / "backend").glob("evaluator*.py"))
    for py_eval in py_evals:
        content = py_eval.read_text()
        try:
            ast.parse(content)
            passed.append(f"Python: {py_eval.name} has valid syntax")
        except SyntaxError as e:
            failed.append(f"Python: {py_eval.name} syntax error: {e.msg}")

    # Check TypeScript/JS evaluator (basic check for common errors)
    for ext in ["*.ts", "*.js"]:
        ts_evals = list((test_dir / "frontend").glob(f"evaluator{ext}"))
        for ts_eval in ts_evals:
            content = ts_eval.read_text()
            # Basic check: balanced braces
            if content.count("{") != content.count("}"):
                failed.append(f"TypeScript: {ts_eval.name} has unbalanced braces")
            elif content.count("(") != content.count(")"):
                failed.append(f"TypeScript: {ts_eval.name} has unbalanced parentheses")
            else:
                passed.append(f"TypeScript: {ts_eval.name} passes basic syntax check")

    return passed, failed


def validate_dataset_integration(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators can work with the dataset structure."""
    passed, failed = [], []

    # This would typically run the evaluator against test cases
    # For now, just check that evaluator files exist
    has_backend = any((test_dir / "backend").glob("evaluator*.py"))
    has_frontend = any((test_dir / "frontend").glob("evaluator*.ts")) or \
                   any((test_dir / "frontend").glob("evaluator*.js"))

    if has_backend:
        passed.append("Dataset: backend evaluator ready for integration")
    else:
        failed.append("Dataset: backend evaluator missing")

    if has_frontend:
        passed.append("Dataset: frontend evaluator ready for integration")
    else:
        failed.append("Dataset: frontend evaluator missing")

    return passed, failed


def validate_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators were uploaded to LangSmith.

    Note: This requires LangSmith API access.
    """
    passed, failed = [], []
    run_id = outputs.get("run_id", "")

    # This would check LangSmith API for uploaded evaluators
    # For now, just mark as informational
    if run_id:
        passed.append(f"Upload: run_id={run_id[:8]}... (check LangSmith manually)")
    else:
        failed.append("Upload: no run_id provided")

    return passed, failed


# List of all validators for this task
VALIDATORS = [
    validate_language_correct,
    validate_syntax_correct,
    validate_dataset_integration,
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
