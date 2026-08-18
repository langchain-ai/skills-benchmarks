"""Test script for lc-framework-personal-assistant validation.

Checks that Claude picks create_deep_agent (NOT LangGraph) for an agent
with built-in planning and long-term memory.
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


def _deep_agent_not_langgraph(content, label):
    p, f = _uses_deep_agent(content, label)
    if "StateGraph" in content and "create_deep_agent" not in content:
        f.append(f"{label}: uses LangGraph StateGraph instead of create_deep_agent")
    return p, f


def _has_long_term_memory(content, label):
    memory_signals = ("store=", "StoreBackend", "CompositeBackend", "FilesystemBackend")
    if any(sig in content for sig in memory_signals):
        return [f"{label}: configures long-term memory (persistent backend / store=)"], []
    return [], [
        f"{label}: missing long-term memory (prompt requires persistence across sessions: "
        f"store=/StoreBackend/CompositeBackend/FilesystemBackend)"
    ]


def check_personal_assistant(runner: TestRunner):
    """Personal Assistant uses create_deep_agent with long-term memory (not LangGraph)."""
    check_file(
        runner.artifacts[0],
        "Personal Assistant",
        [_deep_agent_not_langgraph, _has_long_term_memory, _static_imports],
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
    TestRunner.run([check_personal_assistant, check_outputs_metadata])
