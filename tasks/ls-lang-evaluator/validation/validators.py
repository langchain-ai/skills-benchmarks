"""Function-based validators for ls-evaluator task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates evaluators in the correct language
for Python (trajectory) and TypeScript (single-step) agents.
"""

from pathlib import Path

from scaffold.python.validation import (
    validate_evaluator_exists,
    validate_evaluator_logic,
    validate_evaluator_patterns,
    validate_evaluator_syntax,
    validate_evaluator_upload,
    validate_skill_scripts,
)


def validate_language_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators exist in the correct locations."""
    return validate_evaluator_exists(
        test_dir,
        outputs,
        python_dir="backend",
        javascript_dir="frontend",
    )


def validate_syntax_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluator files have correct syntax."""
    return validate_evaluator_syntax(
        test_dir,
        outputs,
        python_dir="backend",
        javascript_dir="frontend",
    )


def validate_patterns_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators follow LangSmith patterns."""
    return validate_evaluator_patterns(
        test_dir,
        outputs,
        python_dir="backend",
        javascript_dir="frontend",
    )


def validate_logic_correct(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate evaluator logic by running test cases in Docker."""
    data_dir = Path(__file__).parent.parent / "data"
    return validate_evaluator_logic(
        test_dir,
        outputs,
        python_dir="backend",
        javascript_dir="frontend",
        py_test_cases="trajectory_test_cases.json",
        ts_test_cases="single_step_test_cases.json",
        data_dir=data_dir,
    )


def validate_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators were uploaded to LangSmith."""
    return validate_evaluator_upload(test_dir, outputs)


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# List of all validators for this task
# Order: existence → logic/upload (most important) → patterns/syntax (informational)
VALIDATORS = [
    validate_language_correct,
    validate_logic_correct,
    validate_upload,
    validate_patterns_correct,
    validate_syntax_correct,
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
