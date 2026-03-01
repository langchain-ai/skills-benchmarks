"""Test script for lc-basic-noise validation.

Checks SQL agent and search agent code/output, plus noise deliverables.
"""

import ast

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import (
    check_noise_outputs,
    check_skill_invoked,
)
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


def _check_agent_code(runner, filepath, label):
    """Check code patterns and syntax for one agent file."""
    source = runner.read(filepath)
    if not source:
        runner.failed(f"{label}: {filepath} not created")
        return

    runner.passed(f"{label}: {filepath} created")
    try:
        ast.parse(source)
        runner.passed(f"{label}: valid syntax")
    except SyntaxError as e:
        runner.failed(f"{label}: syntax error line {e.lineno}")
        return

    found = [d for p, d in MODERN_PATTERNS.items() if p in source]
    missing = [d for p, d in MODERN_PATTERNS.items() if p not in source]
    if found:
        runner.passed(f"{label}: {', '.join(found[:3])}")
    for d in missing:
        runner.failed(f"{label}: missing {d}")
    for pattern, desc in FORBIDDEN_PATTERNS.items():
        if pattern in source:
            runner.failed(f"{label}: {desc}")


def _check_agent_output(runner, filepath, label, eval_prompt):
    """Run agent and evaluate output quality."""
    output = runner.execute(filepath, timeout=120)
    if output is None:
        return

    if "Traceback" in output and "Error" in output:
        runner.failed(f"{label}: runtime error - {output[:100]}")
        return

    runner.passed(f"{label}: produced output ({len(output)} chars)")
    result = evaluate_with_schema(eval_prompt.format(output=output[:3000]))
    quality = "GOOD" if result["pass"] else "LOW"
    runner.passed(f"{label} quality [{quality}]: {result['reason']}")


def check_sql_agent_code(runner):
    """SQL agent has correct patterns and syntax."""
    _check_agent_code(runner, runner.artifacts[0], "SQL Agent")


def check_sql_agent_output(runner):
    """SQL agent executes and produces quality output."""
    _check_agent_output(
        runner,
        runner.artifacts[0],
        "SQL Agent",
        "Evaluate this program output.\n"
        "Task: SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold\n"
        "Expected: Should show genre names with track counts or sales numbers\n"
        "Output:\n```\n{output}\n```\n"
        "Does this demonstrate the expected behavior?",
    )


def check_search_agent_code(runner):
    """Search agent has correct patterns and syntax."""
    _check_agent_code(runner, runner.artifacts[1], "Search Agent")


def check_search_agent_output(runner):
    """Search agent executes and produces quality output."""
    _check_agent_output(
        runner,
        runner.artifacts[1],
        "Search Agent",
        "Evaluate this program output.\n"
        "Task: Web search agent with mock search tool answering 'What is the capital of France?'\n"
        "Expected: Should return 'Paris' as the answer with proper agent reasoning\n"
        "Output:\n```\n{output}\n```\n"
        "Does this demonstrate the expected behavior?",
    )


def check_metadata(runner):
    """Track skill invocations, metadata, and noise deliverables."""
    events = runner.context.get("events", {})
    runner.passed(f"Turns: {events.get('num_turns', 0) or 0}")
    runner.passed(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    runner.passed(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, _ = check_skill_invoked(runner.context, "langchain-agents", required=False)
    for msg in p:
        runner.passed(msg)

    noise_tasks = runner.context.get("noise_tasks", [])
    if not noise_tasks:
        noise_tasks = ["docker_patterns", "react_components", "api_docs"]
    np, nf = check_noise_outputs(noise_tasks)
    for msg in np:
        runner.passed(msg)
    for msg in nf:
        runner.failed(msg)


if __name__ == "__main__":
    TestRunner.run(
        [
            check_sql_agent_code,
            check_sql_agent_output,
            check_search_agent_code,
            check_search_agent_output,
            check_metadata,
        ]
    )
