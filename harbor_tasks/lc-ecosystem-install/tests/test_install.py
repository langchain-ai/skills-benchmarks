"""Test script for lc-ecosystem-install validation.

Checks that Claude correctly identified the project as a Deep Agents use case
(planning + subagents + persistent memory) and produced:
  - agent.py — code that actually uses the Deep Agents framework
  - install.sh — installs deepagents + langchain-core + langsmith via uv/pip
"""

import re

from scaffold.python.validation.core import (
    check_skill_invoked,
    check_starter_skill_first,
)
from scaffold.python.validation.runner import TestRunner


def _read(filepath):
    try:
        return open(filepath).read()
    except FileNotFoundError:
        return None


def _uses_install_tool(content):
    """Skill says `uv` is recommended but `pip` is also acceptable."""
    if re.search(r"\buv\s+add\b", content):
        return [("Install: uses `uv add` (skill-recommended tool)", True)]
    if re.search(r"\bpip\s+install\b", content):
        return [("Install: uses `pip install` (skill-permitted alternative)", True)]
    return [("Install: no `uv add` or `pip install` command found", False)]


def _has_package(content, package, label):
    if re.search(rf"\b{re.escape(package)}\b", content):
        return [(f"Install: includes {label} (`{package}`)", True)]
    return [(f"Install: missing {label} (`{package}`)", False)]


def check_install_script(runner: TestRunner):
    """install.sh installs deepagents + langchain-core + langsmith via uv/pip."""
    filepath = runner.artifacts[1]  # install.sh
    content = _read(filepath)

    if content is None:
        runner.failed(f"Install: {filepath} not created")
        return
    runner.passed(f"Install: {filepath} created")

    checks = []
    checks.extend(_uses_install_tool(content))
    checks.extend(_has_package(content, "deepagents", "Deep Agents framework"))
    checks.extend(_has_package(content, "langsmith", "LangSmith observability"))

    for msg, ok in checks:
        (runner.passed if ok else runner.failed)(msg)

    # langchain-core is pulled in transitively by deepagents, so a correct
    # `uv add deepagents langsmith` need not list it explicitly — track as a stat.
    for msg, ok in _has_package(content, "langchain-core", "LangChain core"):
        runner.passed(msg if ok else f"Stat: {msg}")


def check_agent_code(runner: TestRunner):
    """agent.py exists and actually uses the Deep Agents framework."""
    filepath = runner.artifacts[0]  # agent.py
    content = _read(filepath)

    if content is None:
        runner.failed(f"Agent: {filepath} not created")
        return
    runner.passed(f"Agent: {filepath} created")

    if re.search(r"\bfrom\s+deepagents\b|\bimport\s+deepagents\b", content):
        runner.passed("Agent: imports `deepagents`")
    else:
        runner.failed(
            "Agent: does not import `deepagents` (Deep Agents is the correct framework for planning+subagents+memory)"
        )

    if re.search(r"\b(?:async_)?create_deep_agent\s*\(", content):
        runner.passed("Agent: calls `create_deep_agent` (or async variant)")
    else:
        runner.failed("Agent: does not call `create_deep_agent`")


def check_outputs_metadata(runner: TestRunner):
    """Read metrics and skill tracking from context (informational, not hard fails)."""
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

    for skill in ("ecosystem-primer", "framework-selection", "langchain-dependencies"):
        p2, _ = check_skill_invoked(runner.context, skill, required=False)
        for msg in p2:
            runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_install_script, check_agent_code, check_outputs_metadata])
