"""Test script for lc-ecosystem-env-setup validation.

Checks that Claude produced a .env.example with the right keys for a new agent
project: ANTHROPIC_API_KEY (named in instruction) plus LangSmith observability
vars (LANGSMITH_API_KEY, LANGSMITH_TRACING=true, LANGSMITH_PROJECT) that come
from the ecosystem primer.
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


def _has_var(content, var):
    if re.search(rf"^\s*#?\s*(?:export\s+)?{re.escape(var)}\s*=", content, re.MULTILINE):
        return [(f"Env: includes `{var}` (commented or active)", True)]
    return [(f"Env: missing `{var}`", False)]


def _has_tracing_true(content):
    match = re.search(
        r"^\s*#?\s*(?:export\s+)?LANGSMITH_TRACING\s*=\s*[\"']?(true|TRUE|True|1)[\"']?\s*$",
        content,
        re.MULTILINE,
    )
    if match:
        return [("Env: `LANGSMITH_TRACING` set to a truthy value (commented or active)", True)]
    if re.search(r"\bLANGSMITH_TRACING\b", content):
        return [("Env: `LANGSMITH_TRACING` present but not set to a truthy value (true/1)", False)]
    return [("Env: missing `LANGSMITH_TRACING`", False)]


def check_env_file(runner: TestRunner):
    """.env.example includes the Anthropic key and LangSmith observability vars."""
    filepath = runner.artifacts[0]
    content = _read(filepath)

    if content is None:
        runner.failed(f"Env: {filepath} not created")
        return
    runner.passed(f"Env: {filepath} created")

    checks = []
    checks.extend(_has_var(content, "ANTHROPIC_API_KEY"))
    checks.extend(_has_var(content, "LANGSMITH_API_KEY"))
    checks.extend(_has_tracing_true(content))

    for msg, ok in checks:
        (runner.passed if ok else runner.failed)(msg)

    # LANGSMITH_PROJECT is documented as optional in the skill — tracked as a
    # stat, not a hard failure.
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

    for skill in ("ecosystem-primer", "framework-selection", "langsmith-trace"):
        p2, _ = check_skill_invoked(runner.context, skill, required=False)
        for msg in p2:
            runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_env_file, check_outputs_metadata])
