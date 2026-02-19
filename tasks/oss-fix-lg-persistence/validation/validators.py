"""Execution-based validators for oss-fix-lg-persistence task.

Each validator runs the actual code and checks behavior, not just patterns.
Returns (passed: list[str], failed: list[str]).
"""

import json
import subprocess
import sys
from pathlib import Path


def _run_test_script(test_dir: Path, agent_path: Path) -> dict:
    """Run the test_persistence.py script against the agent.

    Returns the parsed JSON results.
    """
    test_script = Path(__file__).parent / "test_persistence.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_script), str(agent_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(test_dir),
        )

        # Parse JSON from stdout
        output = result.stdout.strip()
        if output:
            return json.loads(output)
        else:
            return {"error": f"No output from test script. stderr: {result.stderr}"}

    except subprocess.TimeoutExpired:
        return {"error": "Test script timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse test output: {e}"}
    except Exception as e:
        return {"error": f"Failed to run test script: {e}"}


def validate_execution(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run execution tests against the fixed agent code.

    This is the main validator - it actually runs the code and checks behavior.
    """
    passed, failed = [], []

    # Find the agent file (copied to root of test_dir)
    agent_path = test_dir / "broken_agent.py"
    if not agent_path.exists():
        failed.append(f"Agent file not found: {agent_path}")
        return passed, failed

    # Run the test script
    results = _run_test_script(test_dir, agent_path)

    if results.get("error"):
        failed.append(f"Test execution error: {results['error']}")
        return passed, failed

    # Collect results
    passed.extend(results.get("passed", []))
    failed.extend(results.get("failed", []))

    return passed, failed


def validate_checkpointer(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that checkpointer is properly configured."""
    passed, failed = [], []

    # Run full test and filter to checkpointer-related tests
    all_passed, all_failed = validate_execution(test_dir, outputs)

    checkpointer_tests = ["has_checkpointer"]
    for test in checkpointer_tests:
        if test in all_passed:
            passed.append(test)
        elif any(test in f for f in all_failed):
            failed.extend([f for f in all_failed if test in f])

    return passed, failed


def validate_state_persistence(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that state persists correctly across invocations."""
    passed, failed = [], []

    all_passed, all_failed = validate_execution(test_dir, outputs)

    persistence_tests = ["state_persists_across_calls", "thread_isolation"]
    for test in persistence_tests:
        if test in all_passed:
            passed.append(test)
        elif any(test in f for f in all_failed):
            failed.extend([f for f in all_failed if test in f])

    return passed, failed


def validate_state_reducer(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that state reducer is properly configured."""
    passed, failed = [], []

    all_passed, all_failed = validate_execution(test_dir, outputs)

    reducer_tests = ["messages_accumulate_with_reducer"]
    for test in reducer_tests:
        if test in all_passed:
            passed.append(test)
        elif any(test in f for f in all_failed):
            failed.extend([f for f in all_failed if test in f])

    return passed, failed


def validate_functional(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate functional behavior - does the bot actually work?"""
    passed, failed = [], []

    all_passed, all_failed = validate_execution(test_dir, outputs)

    functional_tests = ["remembers_user_name"]
    for test in functional_tests:
        if test in all_passed:
            passed.append(test)
        elif any(test in f for f in all_failed):
            failed.extend([f for f in all_failed if test in f])

    return passed, failed


# List of all validators
VALIDATORS = [
    validate_execution,  # Runs all tests
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run the main execution validator and return results.

    Note: We only run validate_execution once since it covers all tests.
    The individual validators (validate_checkpointer, etc.) are available
    for more granular testing if needed.
    """
    return validate_execution(test_dir, outputs)
