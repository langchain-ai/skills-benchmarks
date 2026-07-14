"""Test script for lc-basic validation.

Checks SQL agent code patterns, syntax, execution, and output quality.
"""

import ast

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import check_skill_invoked
from scaffold.python.validation.runner import TestRunner

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


def check_code(runner: TestRunner):
    """SQL agent has correct patterns and valid syntax."""
    filepath = runner.artifacts[0]
    source = runner.read(filepath)
    if not source:
        runner.failed(f"SQL Agent: {filepath} not created")
        return

    runner.passed(f"SQL Agent: {filepath} created")

    try:
        ast.parse(source)
        runner.passed("SQL Agent: valid syntax")
    except SyntaxError as e:
        runner.failed(f"SQL Agent: syntax error line {e.lineno}")
        return

    found = [d for p, d in MODERN_PATTERNS.items() if p in source]
    missing = [d for p, d in MODERN_PATTERNS.items() if p not in source]
    if found:
        runner.passed(f"SQL Agent: {', '.join(found[:3])}")
    for d in missing:
        runner.failed(f"SQL Agent: missing {d}")

    for pattern, desc in FORBIDDEN_PATTERNS.items():
        if pattern in source:
            runner.failed(f"SQL Agent: {desc}")


def check_output(runner: TestRunner):
    """Agent executes and produces quality output."""
    output = runner.execute(runner.artifacts[0], timeout=120)
    if output is None:
        return

    if "Traceback" in output and "Error" in output:
        runner.failed(f"SQL Agent: runtime error - {output[:100]}")
        return

    runner.passed(f"SQL Agent: produced output ({len(output)} chars)")

    result = evaluate_with_schema(
        f"Evaluate this program output.\n"
        f"Task: SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold\n"
        f"Expected: Should show genre names (Rock, Latin, Metal, etc.) with track counts or sales numbers\n"
        f"Output:\n```\n{output[:3000]}\n```\n"
        f"Does this demonstrate the expected behavior?"
    )
    quality = "GOOD" if result["pass"] else "LOW"
    runner.passed(f"SQL Agent quality [{quality}]: {result['reason']}")


def check_metadata(runner: TestRunner):
    """Track skill invocations and metadata (informational)."""
    events = runner.context.get("events", {})
    runner.passed(f"Turns: {events.get('num_turns', 0) or 0}")
    runner.passed(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    runner.passed(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, _ = check_skill_invoked(runner.context, "langchain-agents", required=False)
    for msg in p:
        runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_code, check_output, check_metadata])
