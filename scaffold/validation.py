"""Function-based validation utilities.

This module provides simple validation functions that can be composed together.
Each function returns (passed: list[str], failed: list[str]).

Usage:
    from scaffold.validation import validate_file_exists, validate_pattern, compose_validators

    # Single check
    passed, failed = validate_file_exists(test_dir, "backend/agent.py")

    # Compose multiple checks
    validator = compose_validators(
        lambda d, o: validate_file_exists(d, "backend/agent.py"),
        lambda d, o: validate_pattern(d / "backend/agent.py", r"@traceable", "has @traceable"),
    )
    passed, failed = validator(test_dir, outputs)
"""

import re
from collections.abc import Callable
from pathlib import Path

# Type alias for validator functions
ValidatorFn = Callable[[Path, dict], tuple[list[str], list[str]]]


def validate_file_exists(test_dir: Path, filepath: str) -> tuple[list[str], list[str]]:
    """Check that a file exists.

    Args:
        test_dir: Test working directory
        filepath: Relative path to file

    Returns:
        (passed, failed) lists
    """
    path = test_dir / filepath
    if path.exists():
        return [f"File exists: {filepath}"], []
    return [], [f"File missing: {filepath}"]


def validate_pattern(
    filepath: Path,
    pattern: str,
    description: str,
    flags: int = 0,
) -> tuple[list[str], list[str]]:
    """Check that a file contains a regex pattern.

    Args:
        filepath: Path to file
        pattern: Regex pattern to search for
        description: Human-readable description of what we're checking
        flags: Regex flags (e.g., re.MULTILINE)

    Returns:
        (passed, failed) lists
    """
    if not filepath.exists():
        return [], [f"{description}: file not found ({filepath.name})"]

    content = filepath.read_text()
    if re.search(pattern, content, flags):
        return [description], []
    return [], [f"Missing: {description}"]


def validate_no_pattern(
    filepath: Path,
    pattern: str,
    description: str,
    flags: int = 0,
) -> tuple[list[str], list[str]]:
    """Check that a file does NOT contain a regex pattern.

    Args:
        filepath: Path to file
        pattern: Regex pattern that should NOT be present
        description: Human-readable description of what we're checking
        flags: Regex flags

    Returns:
        (passed, failed) lists
    """
    if not filepath.exists():
        return [], [f"{description}: file not found ({filepath.name})"]

    content = filepath.read_text()
    if re.search(pattern, content, flags):
        return [], [f"Unexpected: {description}"]
    return [f"No {description}"], []


def validate_function_decorated(
    filepath: Path,
    function_name: str,
    decorator: str,
    language: str = "python",
) -> tuple[list[str], list[str]]:
    """Check that a function has a specific decorator.

    Args:
        filepath: Path to source file
        function_name: Name of function to check
        decorator: Decorator name (without @)
        language: "python" or "typescript"

    Returns:
        (passed, failed) lists
    """
    if not filepath.exists():
        return [], [f"File not found: {filepath.name}"]

    content = filepath.read_text()

    if language == "python":
        # Pattern: @decorator followed by def function_name
        pattern = rf"@{decorator}[^@]*def\s+{function_name}\s*\("
        if re.search(pattern, content, re.DOTALL):
            return [f"Python: {function_name} has @{decorator}"], []

        # Check if function exists but isn't decorated
        if re.search(rf"def\s+{function_name}\s*\(", content):
            return [], [f"Python: {function_name} missing @{decorator}"]
        return [], []  # Function doesn't exist - not necessarily a failure

    elif language == "typescript":
        # Convert snake_case to camelCase
        camel_name = _to_camel_case(function_name)

        # Pattern: const funcName = decorator(
        patterns = [
            rf"const\s+{camel_name}\s*=\s*{decorator}\s*\(",
            rf"const\s+{function_name}\s*=\s*{decorator}\s*\(",
        ]

        if any(re.search(p, content) for p in patterns):
            return [f"TypeScript: {function_name} wrapped with {decorator}()"], []

        # Check if function exists but isn't wrapped
        func_patterns = [
            rf"(const|let|function)\s+{camel_name}\s*[=\(]",
            rf"(const|let|function)\s+{function_name}\s*[=\(]",
        ]
        if any(re.search(p, content) for p in func_patterns):
            return [], [f"TypeScript: {function_name} missing {decorator}()"]
        return [], []

    return [], [f"Unknown language: {language}"]


def _to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def compose_validators(*validators: ValidatorFn) -> ValidatorFn:
    """Compose multiple validator functions into one.

    Args:
        *validators: Validator functions to compose

    Returns:
        A single validator function that runs all validators
    """

    def composed(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
        all_passed, all_failed = [], []
        for validator in validators:
            passed, failed = validator(test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)
        return all_passed, all_failed

    return composed


def run_validators(
    validators: list[ValidatorFn],
    test_dir: Path,
    outputs: dict,
) -> tuple[list[str], list[str]]:
    """Run a list of validator functions.

    Args:
        validators: List of validator functions
        test_dir: Test working directory
        outputs: Additional outputs dict

    Returns:
        Combined (passed, failed) lists
    """
    all_passed, all_failed = [], []
    for validator in validators:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed


# =============================================================================
# TRACING VALIDATORS (for ls-tracing task)
# =============================================================================


def validate_python_tracing(
    test_dir: Path,
    filepath: str = "backend/sql_agent.py",
    required_functions: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate Python LangSmith tracing patterns.

    Checks:
    - Imports traceable from langsmith
    - Imports wrap_openai from langsmith.wrappers
    - Wraps OpenAI client with wrap_openai()
    - Required functions have @traceable decorator
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"Python: {filepath} not found"]

    content = path.read_text()

    # Check imports
    if re.search(r"from\s+langsmith\s+import\s+.*traceable", content, re.IGNORECASE):
        passed.append("Python: imports traceable")
    else:
        failed.append("Python: missing 'from langsmith import traceable'")

    if re.search(r"from\s+langsmith\.wrappers\s+import\s+wrap_openai", content, re.IGNORECASE):
        passed.append("Python: imports wrap_openai")
    else:
        failed.append("Python: missing 'from langsmith.wrappers import wrap_openai'")

    # Check client wrapping
    if re.search(r"wrap_openai\s*\(\s*OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("Python: wraps OpenAI client")
    else:
        failed.append("Python: missing 'wrap_openai(OpenAI())'")

    # Check functions are decorated
    if required_functions:
        traced, untraced = [], []
        for func in required_functions:
            pattern = rf"@traceable[^@]*def\s+{func}\s*\("
            if re.search(pattern, content, re.DOTALL):
                traced.append(func)
            elif re.search(rf"def\s+{func}\s*\(", content):
                untraced.append(func)

        if traced:
            passed.append(f"Python: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            failed.append(f"Python: missing @traceable on: {', '.join(untraced)}")

    return passed, failed


def validate_typescript_tracing(
    test_dir: Path,
    filepath: str = "frontend/support_bot.ts",
    required_functions: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate TypeScript LangSmith tracing patterns.

    Checks:
    - Imports traceable from langsmith/traceable
    - Imports wrapOpenAI from langsmith/wrappers
    - Wraps OpenAI client with wrapOpenAI()
    - Required functions are wrapped with traceable()
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"TypeScript: {filepath} not found"]

    content = path.read_text()

    # Check imports
    if re.search(r'import\s+\{[^}]*traceable[^}]*\}\s+from\s+["\']langsmith/traceable["\']', content):
        passed.append("TypeScript: imports traceable")
    else:
        failed.append("TypeScript: missing 'import { traceable } from \"langsmith/traceable\"'")

    if re.search(r'import\s+\{[^}]*wrapOpenAI[^}]*\}\s+from\s+["\']langsmith/wrappers["\']', content):
        passed.append("TypeScript: imports wrapOpenAI")
    else:
        failed.append("TypeScript: missing 'import { wrapOpenAI } from \"langsmith/wrappers\"'")

    # Check client wrapping
    if re.search(r"wrapOpenAI\s*\(\s*new\s+OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("TypeScript: wraps OpenAI client")
    else:
        failed.append("TypeScript: missing 'wrapOpenAI(new OpenAI())'")

    # Check functions are wrapped
    if required_functions:
        traced, untraced = [], []
        for func in required_functions:
            camel = _to_camel_case(func)
            patterns = [
                rf"const\s+{camel}\s*=\s*traceable\s*\(",
                rf"const\s+{func}\s*=\s*traceable\s*\(",
                rf'name\s*:\s*["\']{func}["\']',
            ]
            if any(re.search(p, content) for p in patterns):
                traced.append(func)
            else:
                func_patterns = [
                    rf"(const|let|function)\s+{camel}\s*[=\(]",
                    rf"async\s+function\s+{camel}\s*\(",
                ]
                if any(re.search(p, content) for p in func_patterns):
                    untraced.append(func)

        if traced:
            passed.append(f"TypeScript: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            failed.append(f"TypeScript: missing traceable() on: {', '.join(untraced)}")

    return passed, failed
