"""Execution-based validators for oss-fix-lc-hitl task.

Each validator runs the actual code and checks behavior, not just patterns.
Returns (passed: list[str], failed: list[str]).
"""

import json
import subprocess
import sys
from pathlib import Path


def _run_test_script(test_dir: Path, agent_path: Path) -> dict:
    """Run the test_hitl.py script against the agent.

    Returns the parsed JSON results.
    """
    test_script = Path(__file__).parent / "test_hitl.py"

    try:
        result = subprocess.run(
            [sys.executable, str(test_script), str(agent_path)],
            capture_output=True,
            text=True,
            timeout=120,
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
    """Run execution tests against the fixed agent code."""
    passed, failed = [], []

    agent_path = test_dir / "broken_agent.py"
    if not agent_path.exists():
        failed.append(f"Agent file not found: {agent_path}")
        return passed, failed

    results = _run_test_script(test_dir, agent_path)

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
