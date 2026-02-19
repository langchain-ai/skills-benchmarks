"""Pattern-based validators for oss-fix-lc-streaming task.

Checks for correct patterns indicating fixes from lc_streaming + lc_tools.
Returns (passed: list[str], failed: list[str]).
"""

import json
import subprocess
import sys
from pathlib import Path


def _run_test_script(test_dir: Path, module_path: Path) -> dict:
    """Run the test_streaming.py script against the chat app.

    Returns the parsed JSON results.
    """
    test_script = Path(__file__).parent / "test_streaming.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_script), str(module_path)],
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
    """Run pattern tests against the fixed chat app code.

    This is the main validator - it checks for correct patterns.
    """
    passed, failed = [], []

    # Find the module file (copied to root of test_dir)
    module_path = test_dir / "chat_app.py"
    if not module_path.exists():
        failed.append(f"Chat app file not found: {module_path}")
        return passed, failed

    # Run the test script
    results = _run_test_script(test_dir, module_path)

    if results.get("error"):
        failed.append(f"Test execution error: {results['error']}")
        return passed, failed

    # Collect results
    passed.extend(results.get("passed", []))
    failed.extend(results.get("failed", []))

    return passed, failed


# List of all validators
VALIDATORS = [
    validate_execution,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run the main execution validator and return results."""
    return validate_execution(test_dir, outputs)
