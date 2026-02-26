"""Function-based validators for ls-evaluator task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude creates evaluators in the correct language
for Python (trajectory) and TypeScript (single-step) agents.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator
from scaffold.python.validation import (
    check_evaluator_upload,
    check_skill_scripts,
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
    return check_evaluator_upload(test_dir, outputs)


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return check_skill_scripts(outputs, events)


# Order: execution checks (most important) → upload → scripts (informational)
VALIDATORS = [
    validate_execution,
    validate_upload,
    validate_scripts,
]
