"""Validate that Claude added LangSmith tracing to the Google ADK agent
AND consulted references/google-adk.md to figure out how.
"""

from pathlib import Path

from scaffold.python.validation.core import check_pattern
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import (
    check_reference_consulted,
    check_skill_scripts,
)
from scaffold.python.validation.tracing import check_langsmith_trace

REFERENCE_FILENAME = "google-adk.md"

GOOGLE_ADK_TRACING_PATTERNS = [
    (
        r"from\s+langsmith\.integrations\.google_adk\s+import\s+configure_google_adk",
        "imports configure_google_adk",
    ),
    (r"configure_google_adk\s*\(", "calls configure_google_adk(...)"),
]


def _events(runner: TestRunner) -> dict:
    return runner.context.get("events", {}) if runner.context else {}


def check_routing(runner: TestRunner) -> None:
    """Hard check: Claude must have read references/google-adk.md."""
    p, f = check_reference_consulted(_events(runner), REFERENCE_FILENAME, required=True)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_google_adk_tracing(runner: TestRunner) -> None:
    """Check that the Google ADK tracing pattern landed in agent.py."""
    filepath = Path(runner.artifacts[0])
    for pattern, desc in GOOGLE_ADK_TRACING_PATTERNS:
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
    TestRunner.run([check_routing, check_google_adk_tracing, check_trace, check_scripts])
