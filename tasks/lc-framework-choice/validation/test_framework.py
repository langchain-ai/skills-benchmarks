"""Test script for lc-framework-choice validation.

Checks that Claude picks the right framework for each component:
- qa_agent.py: simple agent → create_agent (NOT create_react_agent)
- approval_pipeline.py: deterministic routing → LangGraph StateGraph
- middleware_agent.py: hooks/middleware → create_agent or create_deep_agent (NOT LangGraph)
- research_assistant.py: sub-agents + planning → create_deep_agent
- personal_assistant.py: planning + memory → create_deep_agent

Usage: python test_framework.py <qa_agent> <approval_pipeline> <middleware_agent> <research_assistant> <personal_assistant>
"""

import ast
import json
import sys

from scaffold.python.validation.core import (
    check_skill_invoked,
    check_starter_skill_first,
    load_test_context,
    write_test_results,
)


def check_file(filepath, label, checks):
    """Generic file checker: syntax + pattern checks."""
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"{label}: {filepath} not created"]

    passed.append(f"{label}: {filepath} created")

    try:
        ast.parse(content)
        passed.append(f"{label}: valid syntax")
    except SyntaxError as e:
        failed.append(f"{label}: syntax error line {e.lineno}")
        return passed, failed

    for check_fn in checks:
        p, f = check_fn(content, label)
        passed.extend(p)
        failed.extend(f)

    return passed, failed


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

    p, f = check_starter_skill_first(outputs)
    passed.extend(p)
    p2, _ = check_skill_invoked(outputs, "framework-selection", required=False)
    passed.extend(p2)

    return passed, f


def run_tests(*files):
    passed, failed = [], []

    file_checks = [
        (
            files[0] if len(files) > 0 else "qa_agent.py",
            "QA Agent",
            [_uses_create_agent, _no_react_agent, _no_stategraph],
        ),
        (
            files[1] if len(files) > 1 else "approval_pipeline.py",
            "Approval Pipeline",
            [_uses_stategraph],
        ),
        (
            files[2] if len(files) > 2 else "middleware_agent.py",
            "Middleware Agent",
            [_uses_agent_not_langgraph],
        ),
        (
            files[3] if len(files) > 3 else "research_assistant.py",
            "Research Assistant",
            [_uses_deep_agent],
        ),
        (
            files[4] if len(files) > 4 else "personal_assistant.py",
            "Personal Assistant",
            [_deep_agent_not_langgraph],
        ),
    ]

    for filepath, label, checks in file_checks:
        p, f = check_file(filepath, label, checks)
        passed.extend(p)
        failed.extend(f)

    p, f = check_outputs_metadata()
    passed.extend(p)
    failed.extend(f)

    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    results = run_tests(*sys.argv[1:])
    print(json.dumps(results, indent=2))
    write_test_results(results)
    sys.exit(1 if results["failed"] else 0)
