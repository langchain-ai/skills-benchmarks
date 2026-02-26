"""Test script for lc-basic-noise validation.

Checks SQL agent and search agent code/output, plus noise deliverables.

Usage: python test_agents.py <sql_agent_file> <search_agent_file>
"""

import ast
import json
import subprocess
import sys

from scaffold.python.utils import evaluate_with_schema
from scaffold.python.validation.core import validate_noise_outputs, validate_skill_invoked

MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "create_agent(": "uses create_agent",
    "@tool": "@tool decorator",
}

FORBIDDEN_PATTERNS = {
    "from langchain_community.agent_toolkits import create_sql_agent": "imports deprecated create_sql_agent toolkit",
    "from langgraph.prebuilt import create_react_agent": "imports deprecated create_react_agent",
    "create_react_agent(": "uses deprecated create_react_agent",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
}


def check_agent_code(filepath, label):
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"{label}: {filepath} not created"]

    passed.append(f"{label}: {filepath} created")
    try:
        ast.parse(content)
        passed.append(f"{label}: valid syntax")
    except SyntaxError as e:
        failed.append(f"{label}: syntax error line {e.lineno}")
        return passed, failed

    found = [d for p, d in MODERN_PATTERNS.items() if p in content]
    missing = [d for p, d in MODERN_PATTERNS.items() if p not in content]
    if found:
        passed.append(f"{label}: {', '.join(found[:3])}")
    if missing:
        failed.extend(f"{label}: missing {d}" for d in missing)
    for pattern, desc in FORBIDDEN_PATTERNS.items():
        if pattern in content:
            failed.append(f"{label}: {desc}")
    return passed, failed


def check_agent_output(filepath, label, eval_prompt):
    passed, failed = [], []
    try:
        r = subprocess.run(["python", filepath], capture_output=True, text=True, timeout=120)
    except Exception as e:
        return [], [f"{label}: execution error - {str(e)[:80]}"]

    if r.returncode != 0:
        return [], [f"{label}: runtime error - {(r.stderr or r.stdout)[:100]}"]

    output = r.stdout
    passed.append(f"{label}: produced output ({len(output)} chars)")
    result = evaluate_with_schema(eval_prompt.format(output=output[:3000]))
    quality = "GOOD" if result["pass"] else "LOW"
    passed.append(f"{label} quality [{quality}]: {result['reason']}")
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

    p, _ = validate_skill_invoked(outputs, "langchain-agents", required=False)
    passed.extend(p)

    # Check noise deliverables
    noise_tasks = outputs.get("noise_tasks", [])
    if not noise_tasks:
        noise_tasks = ["docker_patterns", "react_components", "api_docs"]
    np, nf = validate_noise_outputs(noise_tasks)
    passed.extend(np)
    failed.extend(nf)

    return passed, failed


def run_tests(sql_file, search_file):
    passed, failed = [], []
    for p, f in [
        check_agent_code(sql_file, "SQL Agent"),
        check_agent_output(
            sql_file,
            "SQL Agent",
            "Evaluate this program output.\n"
            "Task: SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold\n"
            "Expected: Should show genre names with track counts or sales numbers\n"
            "Output:\n```\n{output}\n```\n"
            "Does this demonstrate the expected behavior?",
        ),
        check_agent_code(search_file, "Search Agent"),
        check_agent_output(
            search_file,
            "Search Agent",
            "Evaluate this program output.\n"
            "Task: Web search agent with mock search tool answering 'What is the capital of France?'\n"
            "Expected: Should return 'Paris' as the answer with proper agent reasoning\n"
            "Output:\n```\n{output}\n```\n"
            "Does this demonstrate the expected behavior?",
        ),
        check_outputs_metadata(),
    ]:
        passed.extend(p)
        failed.extend(f)
    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_agents.py <sql_agent> <search_agent>")
        sys.exit(1)
    results = run_tests(sys.argv[1], sys.argv[2])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["failed"] else 0)
