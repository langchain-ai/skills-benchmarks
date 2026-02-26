"""Execution-based validators for oss-fix-lg-execution task.

Each validator runs the actual code and checks behavior, not just patterns.
Returns (passed: list[str], failed: list[str]).
"""

import json
import subprocess
import sys
from pathlib import Path


def _run_test_script(test_dir: Path, module_path: Path) -> dict:
    """Run the test_execution.py script against the pipeline.

    Returns the parsed JSON results.
    """
    test_script = Path(__file__).parent / "test_execution.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_script), str(module_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(test_dir),
        )

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
    """Run execution tests against the fixed pipeline code."""
    passed, failed = [], []

    module_path = test_dir / "broken_pipeline.py"
    if not module_path.exists():
        failed.append(f"Pipeline file not found: {module_path}")
        return passed, failed

    results = _run_test_script(test_dir, module_path)

    if results.get("error"):
        failed.append(f"Test execution error: {results['error']}")
        return passed, failed

    passed.extend(results.get("passed", []))
    failed.extend(results.get("failed", []))

    return passed, failed


VALIDATORS = [
    validate_execution,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run the main execution validator and return results."""
    return validate_execution(test_dir, outputs)
