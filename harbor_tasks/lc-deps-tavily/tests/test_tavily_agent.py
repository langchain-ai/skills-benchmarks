"""Test script for lc-deps-tavily validation.

Checks fixed agent has correct Tavily imports, syntax, and output.
"""

import ast

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import (
    check_skill_invoked,
    check_starter_skill_first,
)
from scaffold.python.validation.runner import TestRunner

CORRECT_IMPORTS = [
    "from langchain_tavily import TavilySearch",
    "from langchain_tavily import TavilySearchResults",
    "from langchain.tools import TavilySearchResults",
]
CORRECT_TOOLS = ["TavilySearch", "TavilySearchResults"]
WRONG_IMPORTS = {
    "from langchain_community.tools.tavily_search": "uses deprecated community tavily import",
    "tavily-python": "uses raw tavily-python instead of langchain-tavily integration",
}


def check_syntax(runner: TestRunner):
    """Agent file exists and has valid syntax."""
    source = runner.read(runner.artifacts[0])
    if not source:
        runner.failed(f"Agent: {runner.artifacts[0]} not created")
        return
    runner.passed(f"Agent: {runner.artifacts[0]} created")
    try:
        ast.parse(source)
        runner.passed("Agent: valid syntax")
    except SyntaxError as e:
        runner.failed(f"Agent: syntax error line {e.lineno}")


def check_imports(runner: TestRunner):
    """Uses correct Tavily import path, not deprecated ones."""
    source = runner.read(runner.artifacts[0])
    if not source:
        runner.failed("Agent: cannot check imports (file missing)")
        return

    if any(p in source for p in CORRECT_IMPORTS):
        imp = next(p for p in CORRECT_IMPORTS if p in source)
        runner.passed(f"Agent: uses {imp}")
    else:
        runner.failed("Agent: missing correct Tavily import path")

    if any(t in source for t in CORRECT_TOOLS):
        runner.passed("Agent: uses Tavily search tool")
    else:
        runner.failed("Agent: missing Tavily search tool usage")

    for pattern, desc in WRONG_IMPORTS.items():
        if pattern in source:
            runner.failed(f"Agent: {desc}")


def check_output(runner: TestRunner):
    """Agent executes and produces meaningful output."""
    output = runner.execute(runner.artifacts[0], timeout=120)
    if output is None:
        return  # execute() already recorded failure

    # Check for runtime errors (non-zero exit returns stdout+stderr)
    if "Traceback" in output and "Error" in output:
        runner.failed(f"Agent: runtime error - {output[:100]}")
        return

    runner.passed(f"Agent: produced output ({len(output)} chars)")

    result = evaluate_with_schema(
        f"Evaluate this program output.\n"
        f'Task: LangChain agent using Tavily web search to answer "What is LangChain?"\n'
        f"Expected: Should return a response about LangChain (framework description, features, etc.)\n"
        f"Output:\n```\n{output[:3000]}\n```\n"
        f"Does this demonstrate the expected behavior?"
    )
    quality = "GOOD" if result["pass"] else "LOW"
    runner.passed(f"Agent quality [{quality}]: {result['reason']}")


def check_metadata(runner: TestRunner):
    """Track skill invocations and metadata (informational)."""
    events = runner.context.get("events", {})
    runner.passed(f"Turns: {events.get('num_turns', 0) or 0}")
    runner.passed(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    runner.passed(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, f = check_starter_skill_first(runner.context)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)

    p2, _ = check_skill_invoked(runner.context, "langchain-dependencies", required=False)
    for msg in p2:
        runner.passed(msg)


if __name__ == "__main__":
    TestRunner.run([check_syntax, check_imports, check_output, check_metadata])
