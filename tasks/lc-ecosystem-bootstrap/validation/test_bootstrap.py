"""Test script for lc-ecosystem-bootstrap validation.

Checks that Claude (a) picked LangGraph from a branching+HITL cue, (b) produced
install.sh with the right packages including LangSmith, and (c) produced
.env.example with LangSmith observability vars.
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


def _has(content, pattern, label_pass, label_fail, flags=0):
    if re.search(pattern, content, flags):
        return [(label_pass, True)]
    return [(label_fail, False)]


def _has_package(content, package, label):
    return _has(
        content,
        rf"\b{re.escape(package)}\b",
        f"Install: includes {label} (`{package}`)",
        f"Install: missing {label} (`{package}`)",
    )


def _has_env_var(content, var):
    return _has(
        content,
        rf"^\s*#?\s*(?:export\s+)?{re.escape(var)}\s*=",
        f"Env: includes `{var}` (commented or active)",
        f"Env: missing `{var}`",
        re.MULTILINE,
    )


def check_install_script(runner: TestRunner):
    """install.sh installs langgraph + langchain-core + langsmith + anthropic via uv."""
    filepath = runner.artifacts[0]
    content = _read(filepath)

    if content is None:
        runner.failed(f"Install: {filepath} not created")
        return
    runner.passed(f"Install: {filepath} created")

    checks = []
    # Skill says `uv` is recommended but `pip` is also acceptable.
    if re.search(r"\buv\s+add\b", content):
        checks.append(("Install: uses `uv add` (skill-recommended tool)", True))
    elif re.search(r"\bpip\s+install\b", content):
        checks.append(("Install: uses `pip install` (skill-permitted alternative)", True))
    else:
        checks.append(("Install: no `uv add` or `pip install` command found", False))

    checks.extend(_has_package(content, "langgraph", "LangGraph framework"))
    checks.extend(_has_package(content, "langchain-core", "LangChain core"))
    checks.extend(_has_package(content, "langsmith", "LangSmith observability"))

    # Provider — instruction names Anthropic.
    if re.search(r"\blangchain-anthropic\b", content):
        checks.append(("Install: includes Anthropic provider (`langchain-anthropic`)", True))
    else:
        other = re.search(r"\blangchain-(openai|google-genai|aws|azure|cohere|mistralai)\b", content)
        if other:
            checks.append((
                f"Install: includes `{other.group(0)}` but instruction names Anthropic — expected `langchain-anthropic`",
                False,
            ))
        else:
            checks.append((
                "Install: missing `langchain-anthropic` (instruction specifies Anthropic models)",
                False,
            ))

    # Negative — should not install deepagents for a LangGraph project.
    if re.search(r"\bdeepagents\b", content):
        checks.append((
            "Install: installs `deepagents` — not needed for a LangGraph project (cue: branching + HITL)",
            False,
        ))

    for msg, ok in checks:
        (runner.passed if ok else runner.failed)(msg)


def check_env_file(runner: TestRunner):
    """.env.example includes the Anthropic key and LangSmith observability vars."""
    filepath = runner.artifacts[1]
    content = _read(filepath)

    if content is None:
        runner.failed(f"Env: {filepath} not created")
        return
    runner.passed(f"Env: {filepath} created")

    checks = []
    checks.extend(_has_env_var(content, "ANTHROPIC_API_KEY"))
    checks.extend(_has_env_var(content, "LANGSMITH_API_KEY"))

    if re.search(
        r"^\s*#?\s*(?:export\s+)?LANGSMITH_TRACING\s*=\s*[\"']?(true|TRUE|True|1)[\"']?\s*$",
        content,
        re.MULTILINE,
    ):
        checks.append(("Env: `LANGSMITH_TRACING` set to a truthy value (commented or active)", True))
    elif re.search(r"\bLANGSMITH_TRACING\b", content):
        checks.append(("Env: `LANGSMITH_TRACING` present but not set to a truthy value (true/1)", False))
    else:
        checks.append(("Env: missing `LANGSMITH_TRACING`", False))

    for msg, ok in checks:
        (runner.passed if ok else runner.failed)(msg)

    if re.search(r"^\s*#?\s*(?:export\s+)?LANGSMITH_PROJECT\s*=", content, re.MULTILINE):
        runner.passed("Env: includes optional `LANGSMITH_PROJECT` (commented or active)")


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

    for skill in (
        "ecosystem-primer",
        "framework-selection",
        "langchain-dependencies",
        "langgraph-fundamentals",
    ):
        p2, _ = check_skill_invoked(runner.context, skill, required=False)
        for msg in p2:
            runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_install_script, check_env_file, check_outputs_metadata])
