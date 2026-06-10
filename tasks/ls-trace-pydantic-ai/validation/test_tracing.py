"""Validate that Claude added LangSmith tracing to the PydanticAI agent
AND consulted references/pydantic-ai.md to figure out how.
"""

from pathlib import Path

from scaffold.python.validation.core import check_pattern
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import (
    check_reference_consulted,
    check_skill_scripts,
)
from scaffold.python.validation.tracing import check_langsmith_trace

REFERENCE_FILENAME = "pydantic-ai.md"

PYDANTIC_AI_TRACING_PATTERNS = [
    (
        r"from\s+langsmith\.integrations\.otel\s+import\s+configure",
        "imports configure from langsmith.integrations.otel",
    ),
    (
        r"from\s+pydantic_ai\s+import\s+[^\n]*Agent",
        "imports Agent from pydantic_ai",
    ),
    (r"configure\s*\(", "calls configure(...)"),
    (r"Agent\.instrument_all\s*\(\s*\)", "calls Agent.instrument_all()"),
]


def _events(runner: TestRunner) -> dict:
    return runner.context.get("events", {}) if runner.context else {}


def check_routing(runner: TestRunner) -> None:
    """Hard check: Claude must have read references/pydantic-ai.md."""
    p, f = check_reference_consulted(_events(runner), REFERENCE_FILENAME, required=True)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_pydantic_ai_tracing(runner: TestRunner) -> None:
    """Check that the PydanticAI tracing pattern landed in agent.py."""
    filepath = Path(runner.artifacts[0])
    for pattern, desc in PYDANTIC_AI_TRACING_PATTERNS:
        p, f = check_pattern(filepath, pattern, f"Python: {desc}")
        for msg in p:
            runner.passed(msg)
        for msg in f:
            runner.failed(msg)


def check_trace(runner: TestRunner) -> None:
    """If Claude saved trace_id.txt, verify the trace exists in LangSmith."""
    p, f = check_langsmith_trace(Path("."), runner.context, trace_id_file="trace_id.txt")
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_scripts(runner: TestRunner) -> None:
    """Track which langsmith CLI commands Claude used (informational)."""
    p, f = check_skill_scripts(runner.context, _events(runner))
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


if __name__ == "__main__":
    TestRunner.run([check_routing, check_pydantic_ai_tracing, check_trace, check_scripts])
