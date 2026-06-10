"""Validate that Claude added LangSmith OTel tracing to the CrewAI agent
AND consulted references/crewai.md to figure out how.
"""

from pathlib import Path

from scaffold.python.validation.core import check_pattern
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import (
    check_reference_consulted,
    check_skill_scripts,
)
from scaffold.python.validation.tracing import check_langsmith_trace

REFERENCE_FILENAME = "crewai.md"

CREWAI_TRACING_PATTERNS = [
    (
        r"from\s+langsmith\.integrations\.otel\s+import\s+OtelSpanProcessor",
        "imports OtelSpanProcessor",
    ),
    (
        r"from\s+opentelemetry\.sdk\.trace\s+import\s+TracerProvider",
        "imports TracerProvider",
    ),
    (
        r"from\s+opentelemetry\.instrumentation\.crewai\s+import\s+CrewAIInstrumentor",
        "imports CrewAIInstrumentor",
    ),
    (
        r"from\s+opentelemetry\.instrumentation\.openai\s+import\s+OpenAIInstrumentor",
        "imports OpenAIInstrumentor",
    ),
    (r"OtelSpanProcessor\s*\(", "instantiates OtelSpanProcessor"),
    (
        r"CrewAIInstrumentor\s*\(\s*\)\s*\.\s*instrument\s*\(\s*tracer_provider\s*=",
        "calls CrewAIInstrumentor().instrument(tracer_provider=...)",
    ),
    (
        r"OpenAIInstrumentor\s*\(\s*\)\s*\.\s*instrument\s*\(\s*tracer_provider\s*=",
        "calls OpenAIInstrumentor().instrument(tracer_provider=...)",
    ),
]


def _events(runner: TestRunner) -> dict:
    return runner.context.get("events", {}) if runner.context else {}


def check_routing(runner: TestRunner) -> None:
    """Hard check: Claude must have read references/crewai.md."""
    p, f = check_reference_consulted(_events(runner), REFERENCE_FILENAME, required=True)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_crewai_tracing(runner: TestRunner) -> None:
    """Check that the CrewAI-specific OTel tracing pattern landed in agent.py."""
    filepath = Path(runner.artifacts[0])
    for pattern, desc in CREWAI_TRACING_PATTERNS:
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
    TestRunner.run([check_routing, check_crewai_tracing, check_trace, check_scripts])
