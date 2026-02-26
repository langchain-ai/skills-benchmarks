"""Function-based validators for ls-evaluator task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates evaluators in the correct language
for Python (trajectory) and TypeScript (single-step) agents.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator
from scaffold.python.validation import (
    validate_evaluator_upload,
    validate_skill_scripts,
)

# Runs in Docker: existence, syntax, patterns, logic for both languages
validate_execution = make_execution_validator(
    eval_dir=Path(__file__).parent,
    test_script="test_evaluator.py",
    module_file=["backend", "frontend"],
    data_dir=Path(__file__).parent.parent / "data",
)


# Host-side only (needs LangSmith API)
def validate_upload(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that evaluators were uploaded to LangSmith."""
    return validate_evaluator_upload(test_dir, outputs)


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# Order: execution checks (most important) → upload → scripts (informational)
VALIDATORS = [
    validate_execution,
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
