"""Function-based validators for lc-version-confusion task.

Tests whether Claude builds a simple agent using modern LangChain patterns
(create_agent, @tool) rather than legacy or incorrect patterns
(create_react_agent from LangGraph, AgentExecutor, etc).
"""

import ast
from pathlib import Path

from scaffold.python.utils import evaluate_with_schema, run_python_in_docker
from scaffold.python.validation import validate_skill_invoked

# Modern patterns that SHOULD be present
MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "@tool": "uses @tool decorator",
    "from langchain_tavily import": "uses correct langchain_tavily import (not community)",
}

# Patterns that indicate wrong choices
WRONG_PATTERNS = {
    "from langgraph.prebuilt import create_react_agent": "uses create_react_agent from LangGraph (should use create_agent for simple agent)",
    "from langchain_community.tools.tavily_search import": "uses deprecated community tavily import (should use langchain_tavily)",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
    "from langchain.chat_models import": "uses old chat_models import path (should use langchain_openai)",
}

# Modern import patterns (good signals)
MODERN_IMPORTS = {
    "from langchain_openai import": "uses correct langchain_openai package",
    "from langchain_anthropic import": "uses correct langchain_anthropic package",
}


def validate_agent_code(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate agent uses modern patterns and not legacy/wrong ones."""
    passed, failed = [], []
    path = test_dir / "agent.py"

    if not path.exists():
        return [], ["Agent: agent.py not created"]

    content = path.read_text()
    passed.append("Agent: agent.py created")

    try:
        ast.parse(content)
        passed.append("Agent: valid syntax")
    except SyntaxError as e:
        return passed, failed + [f"Agent: syntax error line {e.lineno}"]

    # Check modern patterns
    for pattern, desc in MODERN_PATTERNS.items():
        if pattern in content:
            passed.append(f"Agent: {desc}")
        else:
            failed.append(f"Agent: missing {desc}")

    # Check for wrong patterns (hard failures)
    for pattern, desc in WRONG_PATTERNS.items():
        if pattern in content:
            failed.append(f"Agent: {desc}")

    # Check modern imports (informational)
    for pattern, desc in MODERN_IMPORTS.items():
        if pattern in content:
            passed.append(f"Agent: {desc}")

    return passed, failed


def validate_agent_output(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Validate agent runs and produces output."""
    path = test_dir / "agent.py"
    if not path.exists():
        return [], []

    success, output = run_python_in_docker(test_dir, "agent.py")
    if not success:
        return [], [f"Agent: runtime error - {output[:200]}"]

    passed = [f"Agent: produced output ({len(output)} chars)"]

    result = evaluate_with_schema(
        f"""Evaluate this agent output.
Task: Simple web search agent answering "What is LangChain?"
Expected: A coherent answer about LangChain with no import or runtime errors.
Output:
```
{output[:3000]}
```
Does this demonstrate the expected behavior?"""
    )
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"Agent quality [{quality}]: {result['reason']}")
    return passed, []


def validate_skill_usage(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Track skill invocation (informational, doesn't fail)."""
    return validate_skill_invoked(outputs, "langchain-oss-primer", required=False)


def validate_metrics(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Collect turn/duration metrics (always passes)."""
    events = outputs.get("events", {}) if outputs else {}
    return [
        f"Turns: {events.get('num_turns', 0) or 0}",
        f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s",
        f"Tool calls: {len(events.get('tool_calls', []))}",
    ], []


VALIDATORS = [
    validate_skill_usage,
    validate_agent_code,
    validate_agent_output,
    validate_metrics,
]
