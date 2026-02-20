"""Function-based validators for lc-basic-claudemd task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task tests effects of CLAUDE.md presence and content on SQL agent creation.
"""

import ast
from pathlib import Path

from scaffold.python.utils import evaluate_with_schema, run_python_in_docker
from scaffold.python.validation import validate_skill_invoked, validate_starter_skill_first

# Required modern patterns - ALL must be present
AGENT_MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "create_agent(": "uses create_agent",
    "@tool": "@tool decorator",
}

# Deprecated patterns (none of these should be present)
AGENT_FORBIDDEN = {
    "from langchain_community.agent_toolkits import create_sql_agent": "imports deprecated create_sql_agent toolkit",
    "from langgraph.prebuilt import create_react_agent": "imports deprecated create_react_agent",
    "create_react_agent(": "uses deprecated create_react_agent",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
}


def validate_sql_agent_code(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate SQL agent code has modern patterns and no deprecated ones."""
    passed, failed = [], []
    path = test_dir / "sql_agent_1.py"

    if not path.exists():
        return [], ["SQL Agent: sql_agent_1.py not created"]

    content = path.read_text()
    passed.append("SQL Agent: sql_agent_1.py created")

    # Check syntax
    try:
        ast.parse(content)
        passed.append("SQL Agent: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"SQL Agent: syntax error line {e.lineno}"]

    # Check required patterns
    found_required = []
    missing_required = []
    for pattern, desc in AGENT_MODERN_PATTERNS.items():
        if pattern in content:
            found_required.append(desc)
        else:
            missing_required.append(desc)

    if found_required:
        passed.append(f"SQL Agent: {', '.join(found_required[:3])}")
    if missing_required:
        failed.extend(f"SQL Agent: missing {desc}" for desc in missing_required)

    # Check forbidden patterns
    for pattern, desc in AGENT_FORBIDDEN.items():
        if pattern in content:
            failed.append(f"SQL Agent: {desc}")

    return passed, failed


def validate_sql_agent_output(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate SQL agent produces correct output."""
    passed, failed = [], []
    path = test_dir / "sql_agent_1.py"

    if not path.exists():
        return [], []  # Already handled by code validator

    success, output = run_python_in_docker(test_dir, "sql_agent_1.py")
    if not success:
        return [], [f"SQL Agent: runtime error - {output[:100]}"]

    passed.append(f"SQL Agent: produced output ({len(output)} chars)")

    # LLM evaluation of output quality
    prompt = f"""Evaluate this program output.
Task: SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold
Expected: Should show genre names (Rock, Latin, Metal, etc.) with track counts or sales numbers
Output:
```
{output[:3000]}
```
Does this demonstrate the expected behavior?"""

    result = evaluate_with_schema(prompt)
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"SQL Agent quality [{quality}]: {result['reason']}")

    return passed, failed


def validate_skill_usage(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track skill invocation (informational, doesn't fail)."""
    return validate_skill_invoked(outputs, "langchain-agents", required=False)


def validate_metrics(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Collect metrics (always passes)."""
    events = outputs.get("events", {}) if outputs else {}
    passed = [
        f"Turns: {events.get('num_turns', 0) or 0}",
        f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s",
        f"Tool calls: {len(events.get('tool_calls', []))}",
    ]

    # Check for deprecated attempts
    deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"]
    dep_count = sum(
        1
        for tc in events.get("tool_calls", [])
        if tc.get("tool") in ("Write", "Edit")
        and any(d in str(tc.get("input", {})) for d in deprecated)
    )
    if dep_count:
        passed.append(f"Deprecated attempts: {dep_count}")

    return passed, []


# List of all validators for this task
VALIDATORS = [
    validate_starter_skill_first,
    validate_skill_usage,
    validate_sql_agent_code,
    validate_sql_agent_output,
    validate_metrics,
]


def run_all_validators(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run all validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in VALIDATORS:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed
