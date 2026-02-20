"""Function-based validators for lc-deps-tavily task.

Each validator is a function that returns (passed: list[str], failed: list[str]).

This task tests whether Claude can fix a broken project with wrong langchain
dependency names and import paths for Tavily web search integration.
"""

import ast
from pathlib import Path

from scaffold.python.utils import evaluate_with_schema, run_python_in_docker
from scaffold.python.validation import validate_skill_invoked

# Correct import patterns for langchain-tavily
CORRECT_TAVILY_IMPORTS = {
    "langchain_tavily": "imports from langchain_tavily package",
    "TavilySearchResults": "uses TavilySearchResults tool",
}

# Wrong/deprecated import patterns that should NOT be present
WRONG_TAVILY_IMPORTS = {
    "from langchain_community.tools.tavily_search": "uses deprecated community tavily import",
    "from langchain.tools import TavilySearchResults": "uses wrong langchain.tools path",
    "tavily-python": "uses raw tavily-python instead of langchain-tavily integration",
}


def validate_fixed_agent_code(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate fixed agent has correct dependency imports and patterns."""
    passed, failed = [], []
    path = test_dir / "fixed_agent.py"

    if not path.exists():
        return [], ["Fixed Agent: fixed_agent.py not created"]

    content = path.read_text()
    passed.append("Fixed Agent: fixed_agent.py created")

    # Check syntax
    try:
        ast.parse(content)
        passed.append("Fixed Agent: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Fixed Agent: syntax error line {e.lineno}"]

    # Check correct import patterns
    found_correct = []
    missing_correct = []
    for pattern, desc in CORRECT_TAVILY_IMPORTS.items():
        if pattern in content:
            found_correct.append(desc)
        else:
            missing_correct.append(desc)

    if found_correct:
        passed.append(f"Fixed Agent: {', '.join(found_correct[:3])}")
    if missing_correct:
        failed.extend(f"Fixed Agent: missing {desc}" for desc in missing_correct)

    # Check wrong import patterns
    for pattern, desc in WRONG_TAVILY_IMPORTS.items():
        if pattern in content:
            failed.append(f"Fixed Agent: {desc}")

    return passed, failed


def validate_fixed_agent_output(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate fixed agent runs and produces output."""
    passed, failed = [], []
    path = test_dir / "fixed_agent.py"

    if not path.exists():
        return [], []  # Already handled by code validator

    success, output = run_python_in_docker(test_dir, "fixed_agent.py")
    if not success:
        return [], [f"Fixed Agent: runtime error - {output[:100]}"]

    passed.append(f"Fixed Agent: produced output ({len(output)} chars)")

    # LLM evaluation of output quality
    prompt = f"""Evaluate this program output.
Task: LangChain agent using Tavily web search to answer "What is LangChain?"
Expected: Should return a response about LangChain (framework description, features, etc.)
Output:
```
{output[:3000]}
```
Does this demonstrate the expected behavior?"""

    result = evaluate_with_schema(prompt)
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"Fixed Agent quality [{quality}]: {result['reason']}")

    return passed, failed


def validate_skill_usage(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track skill invocation (informational, doesn't fail)."""
    return validate_skill_invoked(outputs, "langchain-dependencies", required=False)


def validate_metrics(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Collect metrics (always passes)."""
    events = outputs.get("events", {}) if outputs else {}
    passed = [
        f"Turns: {events.get('num_turns', 0) or 0}",
        f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s",
        f"Tool calls: {len(events.get('tool_calls', []))}",
    ]

    # Check for wrong import attempts
    wrong_imports = ["langchain_community.tools.tavily_search", "tavily-python"]
    wrong_count = sum(
        1
        for tc in events.get("tool_calls", [])
        if tc.get("tool") in ("Write", "Edit")
        and any(d in str(tc.get("input", {})) for d in wrong_imports)
    )
    if wrong_count:
        passed.append(f"Wrong import attempts: {wrong_count}")

    return passed, []


# List of all validators for this task
VALIDATORS = [
    validate_skill_usage,
    validate_fixed_agent_code,
    validate_fixed_agent_output,
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
