"""Test script for lc-basic validation.

Checks SQL agent code patterns, syntax, execution, and output quality.
Reads _test_context.json for metrics and skill tracking.
Runs inside Docker via make_execution_validator.

Usage: python test_sql_agent.py <agent_file>
"""

import ast
import json
import subprocess
import sys

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import (
    check_skill_invoked,
    load_test_context,
    write_test_results,
)

MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "create_agent(": "uses create_agent",
    "@tool": "@tool decorator",
}

FORBIDDEN_PATTERNS = {
    "from langchain_community.agent_toolkits import create_sql_agent": "imports deprecated create_sql_agent toolkit",
    "from langgraph.prebuilt import create_react_agent": "imports deprecated create_react_agent",
    "create_react_agent(": "uses deprecated create_react_agent",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
}


def check_code(filepath):
    """Check code patterns and syntax."""
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"SQL Agent: {filepath} not created"]

    passed.append(f"SQL Agent: {filepath} created")

    try:
        ast.parse(content)
        passed.append("SQL Agent: valid syntax")
    except SyntaxError as e:
        failed.append(f"SQL Agent: syntax error line {e.lineno}")
        return passed, failed

    found = [d for p, d in MODERN_PATTERNS.items() if p in content]
    missing = [d for p, d in MODERN_PATTERNS.items() if p not in content]
    if found:
        passed.append(f"SQL Agent: {', '.join(found[:3])}")
    if missing:
        failed.extend(f"SQL Agent: missing {d}" for d in missing)

    for pattern, desc in FORBIDDEN_PATTERNS.items():
        if pattern in content:
            failed.append(f"SQL Agent: {desc}")

    return passed, failed


def check_output(filepath):
    """Run agent and evaluate output quality."""
    passed, failed = [], []
    try:
        r = subprocess.run([sys.executable, filepath], capture_output=True, text=True, timeout=120)
    except Exception as e:
        return [], [f"SQL Agent: execution error - {str(e)[:80]}"]

    if r.returncode != 0:
        return [], [f"SQL Agent: runtime error - {(r.stderr or r.stdout)[:100]}"]

    output = r.stdout
    passed.append(f"SQL Agent: produced output ({len(output)} chars)")

    result = evaluate_with_schema(
        f"Evaluate this program output.\n"
        f"Task: SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold\n"
        f"Expected: Should show genre names (Rock, Latin, Metal, etc.) with track counts or sales numbers\n"
        f"Output:\n```\n{output[:3000]}\n```\n"
        f"Does this demonstrate the expected behavior?"
    )
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"SQL Agent quality [{quality}]: {result['reason']}")

    return passed, failed


def check_outputs_metadata():
    """Read metrics and skill tracking from _test_context.json."""
    passed = []
    try:
        outputs = load_test_context()
    except (FileNotFoundError, json.JSONDecodeError):
        return passed, []

    events = outputs.get("events", {})
    passed.append(f"Turns: {events.get('num_turns', 0) or 0}")
    passed.append(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    passed.append(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, _ = check_skill_invoked(outputs, "langchain-agents", required=False)
    passed.extend(p)

    return passed, []


def run_tests(agent_file):
    passed, failed = [], []
    for p, f in [
        check_code(agent_file),
        check_output(agent_file),
        check_outputs_metadata(),
    ]:
        passed.extend(p)
        failed.extend(f)
    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_sql_agent.py <agent_file>")
        sys.exit(1)
    results = run_tests(sys.argv[1])
    print(json.dumps(results, indent=2))
    write_test_results(results)
    sys.exit(1 if results["failed"] else 0)
