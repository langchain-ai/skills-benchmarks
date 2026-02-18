"""Function-based validators for ls-tracing task.

Each validator is a function that returns (passed: list[str], failed: list[str]).
"""

import re
from pathlib import Path

from scaffold.validation import validate_python_tracing, validate_typescript_tracing

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


def validate_language_syntax(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that each file uses correct language syntax (no mixing)."""
    passed, failed = [], []

    # Python-only patterns (shouldn't appear in TypeScript)
    py_only = [
        (r"^def\s+\w+\s*\(", "Python def"),
        (r"^@\w+", "Python decorator"),
    ]

    # TypeScript-only patterns (shouldn't appear in Python)
    ts_only = [
        (r":\s*(string|number|boolean|Promise<)", "TypeScript type annotation"),
        (r"^(const|let)\s+\w+\s*=", "TypeScript const/let"),
    ]

    # Check Python file
    py_path = test_dir / "backend/sql_agent.py"
    if py_path.exists():
        content = py_path.read_text()
        for pattern, desc in ts_only:
            if re.search(pattern, content, re.MULTILINE):
                failed.append(f"Python file has {desc}")
        if not failed:
            passed.append("Python: correct syntax")

    # Check TypeScript file
    ts_path = test_dir / "frontend/support_bot.ts"
    if ts_path.exists():
        content = ts_path.read_text()
        for pattern, desc in py_only:
            if re.search(pattern, content, re.MULTILINE):
                failed.append(f"TypeScript file has {desc}")
        if "TypeScript" not in "".join(failed):
            passed.append("TypeScript: correct syntax")

    return passed, failed


def validate_code_execution(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that the code runs without errors.

    Note: This is a placeholder - actual execution requires Docker.
    """
    passed, failed = [], []

    # Check files exist
    py_path = test_dir / "backend/sql_agent.py"
    ts_path = test_dir / "frontend/support_bot.ts"

    if py_path.exists():
        passed.append("Python file exists")
    else:
        failed.append("Python file missing")

    if ts_path.exists():
        passed.append("TypeScript file exists")
    else:
        failed.append("TypeScript file missing")

    return passed, failed


def validate_langsmith_trace(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that a trace was created in LangSmith.

    Note: This requires LangSmith API access.
    """
    passed, failed = [], []

    # Check for trace_id.txt file
    trace_file = test_dir / "trace_id.txt"
    if trace_file.exists():
        trace_id = trace_file.read_text().strip()
        if trace_id:
            passed.append(f"Trace ID saved: {trace_id[:8]}...")
        else:
            failed.append("trace_id.txt is empty")
    else:
        failed.append("trace_id.txt not found")

    return passed, failed


# List of all validators for this task
VALIDATORS = [
    validate_tracing_patterns,
    validate_language_syntax,
    validate_code_execution,
    validate_langsmith_trace,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run all validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in VALIDATORS:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed
