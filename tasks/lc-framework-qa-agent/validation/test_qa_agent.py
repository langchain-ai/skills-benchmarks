"""Test script for lc-framework-qa-agent validation.

Checks that Claude picks create_agent (NOT create_react_agent or StateGraph)
for a basic react agent.
"""

import ast
from io import StringIO

from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter

from scaffold.python.validation.core import (
    check_skill_invoked,
    check_starter_skill_first,
)
from scaffold.python.validation.runner import TestRunner


def check_file(filepath, label, checks, runner: TestRunner):
    """Generic file checker: syntax + pattern checks."""
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        runner.failed(f"{label}: {filepath} not created")
        return

    runner.passed(f"{label}: {filepath} created")

    try:
        ast.parse(content)
        runner.passed(f"{label}: valid syntax")
    except SyntaxError as e:
        runner.failed(f"{label}: syntax error line {e.lineno}")
        return

    for check_fn in checks:
        p, f = check_fn(content, label)
        for msg in p:
            runner.passed(msg)
        for msg in f:
            runner.failed(msg)


def _static_imports(content, label):
    """Run pyflakes and surface only 'undefined name' findings as failures."""
    stdout_buf, stderr_buf = StringIO(), StringIO()
    pyflakes_check(content, f"{label}.py", Reporter(stdout_buf, stderr_buf))
    undefined = [line for line in stdout_buf.getvalue().splitlines() if "undefined name" in line]
    if not undefined:
        return [f"{label}: no undefined names (imports resolve)"], []
    return [], [f"{label}: undefined names — {'; '.join(undefined)}"]


def _uses_create_agent(content, label):
    if "from langchain.agents import create_agent" in content:
        return [f"{label}: correctly uses create_agent"], []
    return [], [f"{label}: missing create_agent from langchain.agents"]


def _no_react_agent(content, label):
    if "from langgraph.prebuilt import create_react_agent" in content:
        return [], [
            f"{label}: uses create_react_agent from LangGraph (should use create_agent for simple agent)"
        ]
    return [], []


def _no_stategraph(content, label):
    if "StateGraph" in content:
        return [], [f"{label}: uses LangGraph StateGraph (overkill for simple react agent)"]
    return [], []


def check_qa_agent(runner: TestRunner):
    """QA Agent uses create_agent (not react_agent or StateGraph)."""
    check_file(
        runner.artifacts[0],
        "QA Agent",
        [_uses_create_agent, _no_react_agent, _no_stategraph, _static_imports],
        runner,
    )


def check_outputs_metadata(runner: TestRunner):
    """Read metrics and skill tracking from context."""
    events = runner.context.get("events", {})
    runner.passed(f"Turns: {events.get('num_turns', 0) or 0}")
    runner.passed(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    runner.passed(f"Tool calls: {len(events.get('tool_calls', []))}")

    # Starter-skill check tracked as a stat — agent.py content is the
    # authoritative signal for framework choice.
    p, f = check_starter_skill_first(runner.context)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.passed(f"Stat: {msg}")

    for skill in ("ecosystem-primer", "framework-selection"):
        p2, _ = check_skill_invoked(runner.context, skill, required=False)
        for msg in p2:
            runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_qa_agent, check_outputs_metadata])
