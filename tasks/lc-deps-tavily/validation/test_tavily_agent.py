"""Test script for lc-deps-tavily validation.

Checks fixed agent has correct Tavily imports, syntax, and output.

Usage: python test_tavily_agent.py <agent_file>
"""

import ast
import json
import subprocess
import sys

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import check_skill_invoked, check_starter_skill_first

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


def check_code(filepath):
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"Agent: {filepath} not created"]

    passed.append(f"Agent: {filepath} created")

    try:
        ast.parse(content)
        passed.append("Agent: valid syntax")
    except SyntaxError as e:
        failed.append(f"Agent: syntax error line {e.lineno}")
        return passed, failed

    if any(p in content for p in CORRECT_IMPORTS):
        imp = next(p for p in CORRECT_IMPORTS if p in content)
        passed.append(f"Agent: uses {imp}")
    else:
        failed.append("Agent: missing correct Tavily import path")

    if any(t in content for t in CORRECT_TOOLS):
        passed.append("Agent: uses Tavily search tool")
    else:
        failed.append("Agent: missing Tavily search tool usage")

    for pattern, desc in WRONG_IMPORTS.items():
        if pattern in content:
            failed.append(f"Agent: {desc}")

    return passed, failed


def check_output(filepath):
    passed, failed = [], []
    try:
        r = subprocess.run(["python", filepath], capture_output=True, text=True, timeout=120)
    except Exception as e:
        return [], [f"Agent: execution error - {str(e)[:80]}"]

    if r.returncode != 0:
        return [], [f"Agent: runtime error - {(r.stderr or r.stdout)[:100]}"]

    output = r.stdout
    passed.append(f"Agent: produced output ({len(output)} chars)")

    result = evaluate_with_schema(
        f"Evaluate this program output.\n"
        f'Task: LangChain agent using Tavily web search to answer "What is LangChain?"\n'
        f"Expected: Should return a response about LangChain (framework description, features, etc.)\n"
        f"Output:\n```\n{output[:3000]}\n```\n"
        f"Does this demonstrate the expected behavior?"
    )
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"Agent quality [{quality}]: {result['reason']}")

    return passed, failed


def check_outputs_metadata():
    passed, failed = [], []
    try:
        outputs = json.loads(open("_outputs.json").read())
    except (FileNotFoundError, json.JSONDecodeError):
        return passed, failed

    events = outputs.get("events", {})
    passed.append(f"Turns: {events.get('num_turns', 0) or 0}")
    passed.append(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
    passed.append(f"Tool calls: {len(events.get('tool_calls', []))}")

    p, f = check_starter_skill_first(outputs)
    passed.extend(p)
    failed.extend(f)
    p2, _ = check_skill_invoked(outputs, "langchain-dependencies", required=False)
    passed.extend(p2)

    return passed, failed


def run_tests(agent_file):
    passed, failed = [], []
    for p, f in [check_code(agent_file), check_output(agent_file), check_outputs_metadata()]:
        passed.extend(p)
        failed.extend(f)
    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tavily_agent.py <agent_file>")
        sys.exit(1)
    results = run_tests(sys.argv[1])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["failed"] else 0)
