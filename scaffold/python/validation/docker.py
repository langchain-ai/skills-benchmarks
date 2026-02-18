"""Docker-based code execution validation.

Validates that code runs successfully in Docker containers.
"""

from pathlib import Path

from scaffold.python.utils import run_node_in_docker, run_python_in_docker


def validate_python_execution(
    test_dir: Path,
    filepath: str = "backend/sql_agent.py",
    timeout: int = 120,
    args: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate that Python code runs without errors in Docker.

    Args:
        test_dir: Test working directory (contains Dockerfile)
        filepath: Relative path to Python file
        timeout: Execution timeout in seconds
        args: Optional command-line arguments

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"Python: {filepath} not found"]

    success, output = run_python_in_docker(test_dir, filepath, timeout=timeout, args=args)
    if success:
        passed.append(f"Python: {filepath} executes successfully")
    else:
        error = output[:100] if output else "unknown error"
        failed.append(f"Python: execution failed ({error})")

    return passed, failed


def validate_typescript_execution(
    test_dir: Path,
    filepath: str = "frontend/support_bot.ts",
    timeout: int = 120,
    args: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate that TypeScript code runs without errors in Docker.

    Args:
        test_dir: Test working directory (contains Dockerfile)
        filepath: Relative path to TypeScript file
        timeout: Execution timeout in seconds
        args: Optional command-line arguments

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"TypeScript: {filepath} not found"]

    success, output = run_node_in_docker(test_dir, filepath, timeout=timeout, args=args)
    if success:
        passed.append(f"TypeScript: {filepath} executes successfully")
    else:
        error = output[:100] if output else "unknown error"
        failed.append(f"TypeScript: execution failed ({error})")

    return passed, failed


def validate_code_execution(
    test_dir: Path,
    python_file: str = "backend/sql_agent.py",
    typescript_file: str = "frontend/support_bot.ts",
    timeout: int = 120,
) -> tuple[list[str], list[str]]:
    """Validate that both Python and TypeScript code run without errors.

    Args:
        test_dir: Test working directory (contains Dockerfile)
        python_file: Relative path to Python file
        typescript_file: Relative path to TypeScript file
        timeout: Execution timeout in seconds

    Returns:
        (passed, failed) lists
    """
    all_passed, all_failed = [], []

    # Python execution
    py_passed, py_failed = validate_python_execution(test_dir, python_file, timeout)
    all_passed.extend(py_passed)
    all_failed.extend(py_failed)

    # TypeScript execution
    ts_passed, ts_failed = validate_typescript_execution(test_dir, typescript_file, timeout)
    all_passed.extend(ts_passed)
    all_failed.extend(ts_failed)

    return all_passed, all_failed
