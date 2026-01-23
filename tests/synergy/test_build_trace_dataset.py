#!/usr/bin/env python3
"""Synergy test - chaining multiple skills together."""

import sys
import os
import argparse
from pathlib import Path

skills_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_root))

from scaffold.setup import setup_test_environment, copy_test_data
from scaffold.runner import run_comparison, ContextMode


PROMPT = """Complete this workflow:

1. Create a SQL agent using LangChain that queries chinook.db (use ChatOpenAI gpt-4o-mini)
   Save to sql_agent.py

2. Run the agent with 2-3 test queries to generate traces

3. Query the traces using LangSmith SDK:
   from langsmith import Client
   client.list_runs(project_name="skills", limit=5)

4. Create test_dataset.json from traces with format: [{"inputs": ..., "outputs": ...}]"""


def validate(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Validate pipeline completion."""
    passed, failed = [], []

    # Check agent created
    if (test_dir / "sql_agent.py").exists():
        passed.append("Created agent")
    else:
        failed.append("No agent file")

    # Check dataset created
    json_files = list(test_dir.glob("*.json"))
    if json_files:
        passed.append(f"Created dataset: {json_files[0].name}")
    else:
        failed.append("No dataset file")

    # Check tool usage
    tools_used = {tc["tool"] for tc in events.get("tool_calls", [])}
    if "Bash" in tools_used:
        passed.append("Ran commands")
    if "Write" in tools_used:
        passed.append("Wrote files")

    return passed, failed


def make_dir():
    test_dir = setup_test_environment()
    chinook = skills_root / "tests" / "langchain-agents" / "chinook.db"
    if chinook.exists():
        copy_test_data(chinook, test_dir)
    return test_dir


def run(model: str = None):
    print("SYNERGY TEST: Build → Trace → Dataset\n")

    results = run_comparison(
        name="Pipeline",
        prompt=PROMPT,
        make_dir=make_dir,
        validate=validate,
        modes=[ContextMode.NONE, ContextMode.FULL],
        timeout=600,
        model=model,
    )

    # Analysis
    none = results.get(ContextMode.NONE)
    full = results.get(ContextMode.FULL)
    if none and full:
        diff = len(full.checks_passed) - len(none.checks_passed)
        print(f"\nSYNERGY: {'improved' if diff > 0 else 'no change' if diff == 0 else 'hurt'} by {abs(diff)} checks")

    return 0 if any(r.passed for r in results.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    sys.exit(run(model=args.model))
