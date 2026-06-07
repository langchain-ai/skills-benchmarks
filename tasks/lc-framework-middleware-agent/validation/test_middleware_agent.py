"""Test script for lc-framework-middleware-agent validation.

Checks that Claude picks create_agent or create_deep_agent (NOT LangGraph
StateGraph) for a hooks/middleware pattern.
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


def _uses_agent_not_langgraph(content, label):
    p, f = [], []
    uses_create_agent = "create_agent" in content
    uses_deep_agent = "create_deep_agent" in content
    uses_langgraph = "StateGraph" in content
    if uses_langgraph:
        f.append(
            f"{label}: uses LangGraph StateGraph (middleware/hooks are not a LangGraph concept)"
        )
    if uses_create_agent or uses_deep_agent:
        which = "create_agent" if uses_create_agent else "create_deep_agent"
        p.append(f"{label}: correctly uses {which} for hook/middleware pattern")
    elif not uses_langgraph:
        f.append(f"{label}: missing create_agent or create_deep_agent")
    hook_signals = (
        "middleware=",
        "AgentMiddleware",
        "@before_agent",
        "@before_model",
        "@after_model",
        "@after_agent",
        "@wrap_model_call",
    )
    if any(sig in content for sig in hook_signals):
        p.append(f"{label}: implements pre/post hooks via middleware")
    else:
        f.append(
            f"{label}: missing middleware/hooks (prompt requires pre/post hooks around the agent)"
        )
    return p, f


def check_middleware_agent(runner: TestRunner):
    """Middleware Agent uses create_agent or create_deep_agent (not LangGraph)."""
    check_file(
        runner.artifacts[0],
        "Middleware Agent",
        [_uses_agent_not_langgraph, _static_imports],
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
    TestRunner.run([check_middleware_agent, check_outputs_metadata])
