"""Test script for lc-framework-research-assistant validation.

Checks that Claude picks create_deep_agent for an open-ended planner that
delegates to specialized sub-agents.
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


def _uses_deep_agent(content, label):
    if "create_deep_agent" in content:
        return [f"{label}: correctly uses create_deep_agent"], []
    return [], [f"{label}: missing create_deep_agent"]


def _delegates_to_subagents(content, label):
    if "subagents=" in content:
        return [f"{label}: delegates to specialized sub-agents (subagents=)"], []
    return [], [
        f"{label}: missing subagents= (prompt requires delegation to specialized sub-agents)"
    ]


def check_research_assistant(runner: TestRunner):
    """Research Assistant uses create_deep_agent with delegated sub-agents."""
    check_file(
        runner.artifacts[0],
        "Research Assistant",
        [_uses_deep_agent, _delegates_to_subagents, _static_imports],
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
    TestRunner.run([check_research_assistant, check_outputs_metadata])
