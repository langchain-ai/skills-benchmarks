"""Function-based validators for ls-tracing task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task validates that Claude correctly adds LangSmith tracing to both
Python and TypeScript agents.
"""

from pathlib import Path

from scaffold.python.utils import make_execution_validator
from scaffold.python.validation import (
    check_langsmith_trace,
    check_skill_scripts,
)

# Functions that must be traced
# Note: lookup_order is a @tool function — LangChain auto-traces tools,
# so explicit traceable() is redundant and not required
REQUIRED_FUNCTIONS = [
    "classify_intent",
    "extract_entities",
    "generate_response",
    "handle_support_request",
]

# Runs in Docker: tracing patterns, language syntax, code execution
validate_execution = make_execution_validator(
    validation_dir=Path(__file__).parent,
    test_script="test_tracing.py",
    target_artifacts=["backend/sql_agent.py", "frontend/support_bot.ts"],
)


# Host-side only (needs LangSmith API)
def validate_trace(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate that a trace was created in LangSmith."""
    return check_langsmith_trace(
        test_dir,
        outputs,
        trace_id_file="trace_id.txt",
        expected_functions=REQUIRED_FUNCTIONS,
    )


def validate_scripts(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track which skill scripts Claude used (informational)."""
    events = outputs.get("events", {}) if outputs else {}
    return check_skill_scripts(outputs, events)


VALIDATORS = [
    validate_execution,
    validate_trace,
    validate_scripts,
]
