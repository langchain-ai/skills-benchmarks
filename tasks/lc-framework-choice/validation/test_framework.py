"""Test script for lc-framework-choice validation.

Checks that Claude picks the right framework for each component:
- qa_agent.py: simple agent -> create_agent (NOT create_react_agent)
- approval_pipeline.py: deterministic routing -> LangGraph StateGraph
- middleware_agent.py: hooks/middleware -> create_agent or create_deep_agent (NOT LangGraph)
- research_assistant.py: sub-agents + planning -> create_deep_agent
- personal_assistant.py: planning + memory -> create_deep_agent
"""

import ast

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


def _uses_stategraph(content, label):
    p, f = [], []
    if "StateGraph" in content:
        p.append(f"{label}: correctly uses LangGraph StateGraph for deterministic routing")
    else:
        f.append(f"{label}: missing LangGraph StateGraph (required for deterministic branching)")
    if "add_conditional_edges" in content or "add_edge" in content:
        p.append(f"{label}: uses explicit edge routing")
    return p, f


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
    return p, f


def _uses_deep_agent(content, label):
    if "create_deep_agent" in content:
        return [f"{label}: correctly uses create_deep_agent"], []
    return [], [f"{label}: missing create_deep_agent"]


def _deep_agent_not_langgraph(content, label):
    p, f = _uses_deep_agent(content, label)
    if "StateGraph" in content and "create_deep_agent" not in content:
        f.append(f"{label}: uses LangGraph StateGraph instead of create_deep_agent")
    return p, f


def check_qa_agent(runner: TestRunner):
    """QA Agent uses create_agent (not react_agent or StateGraph)."""
    check_file(
        runner.artifacts[0],
        "QA Agent",
        [_uses_create_agent, _no_react_agent, _no_stategraph],
        runner,
    )


def check_approval_pipeline(runner: TestRunner):
    """Approval Pipeline uses LangGraph StateGraph."""
    check_file(
        runner.artifacts[1],
        "Approval Pipeline",
        [_uses_stategraph],
        runner,
    )


def check_middleware_agent(runner: TestRunner):
    """Middleware Agent uses create_agent or create_deep_agent (not LangGraph)."""
    check_file(
        runner.artifacts[2],
        "Middleware Agent",
        [_uses_agent_not_langgraph],
        runner,
    )


def check_research_assistant(runner: TestRunner):
    """Research Assistant uses create_deep_agent."""
    check_file(
        runner.artifacts[3],
        "Research Assistant",
        [_uses_deep_agent],
        runner,
    )


def check_personal_assistant(runner: TestRunner):
    """Personal Assistant uses create_deep_agent (not LangGraph)."""
    check_file(
        runner.artifacts[4],
        "Personal Assistant",
        [_deep_agent_not_langgraph],
        runner,
    )


def check_outputs_metadata(runner: TestRunner):
    """Read metrics and skill tracking from context."""
    events = runner.context.get("events", {})
    runner.passed(f"Turns: {events.get('num_turns', 0) or 0}")
    runner.passed(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    runner.passed(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, f = check_starter_skill_first(runner.context)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)

    p2, _ = check_skill_invoked(runner.context, "framework-selection", required=False)
    for msg in p2:
        runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run(
        [
            check_qa_agent,
            check_approval_pipeline,
            check_middleware_agent,
            check_research_assistant,
            check_personal_assistant,
            check_outputs_metadata,
        ]
    )
