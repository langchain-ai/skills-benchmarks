"""Function-based validators for ls-tracing task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude correctly adds LangSmith tracing to both
Python and TypeScript agents.
"""

from pathlib import Path

from scaffold.python.validation import (
    validate_code_execution,
    validate_langsmith_trace,
    validate_language_syntax,
    validate_python_tracing,
    validate_skill_scripts,
    validate_typescript_tracing,
)

# Functions that must be traced
REQUIRED_FUNCTIONS = [
    "classify_intent",
    "extract_entities",
    "lookup_order",
    "generate_response",
    "handle_support_request",
]


def validate_tracing_patterns(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate LangSmith tracing patterns in both Python and TypeScript files."""
    all_passed, all_failed = [], []

    # Python validation
    py_passed, py_failed = validate_python_tracing(
        test_dir,
        filepath="backend/sql_agent.py",
        required_functions=REQUIRED_FUNCTIONS,
    )
    all_passed.extend(py_passed)
    all_failed.extend(py_failed)

    # TypeScript validation
    ts_passed, ts_failed = validate_typescript_tracing(
        test_dir,
        filepath="frontend/support_bot.ts",
        required_functions=REQUIRED_FUNCTIONS,
    )
    all_passed.extend(ts_passed)
    all_failed.extend(ts_failed)

    return all_passed, all_failed


def validate_syntax(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that each file uses correct language syntax (no mixing)."""
    return validate_language_syntax(
        test_dir,
        python_file="backend/sql_agent.py",
        typescript_file="frontend/support_bot.ts",
    )


def validate_execution(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the traced code runs without errors in Docker."""
    return validate_code_execution(
        test_dir,
        python_file="backend/sql_agent.py",
        typescript_file="frontend/support_bot.ts",
    )


def validate_trace(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that a trace was created in LangSmith."""
    return validate_langsmith_trace(
        test_dir,
        outputs,
        trace_id_file="trace_id.txt",
        expected_functions=REQUIRED_FUNCTIONS,
    )


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return validate_skill_scripts(test_dir, outputs, events)


# List of all validators for this task
VALIDATORS = [
    validate_tracing_patterns,
    validate_syntax,
    validate_execution,
    validate_trace,
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
