#!/usr/bin/env python3
"""Test whether CLAUDE.md improves pattern usage."""

import sys
import argparse
from pathlib import Path

skills_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_root))

from scaffold.setup import setup_test_environment, copy_test_data
from scaffold.runner import run_comparison, ContextMode
from scaffold.capture import did_read


PROMPT = """Build a Python text-to-SQL agent using LangChain that can query the chinook.db SQLite database.

Requirements:
- Use gpt-4o-mini
- Only allow SELECT queries
- Include error handling

Save to sql_agent.py and run a test query."""


def validate(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Validate generated code patterns."""
    passed, failed = [], []

    agent_file = test_dir / "sql_agent.py"
    if not agent_file.exists():
        return passed, ["sql_agent.py not created"]

    content = agent_file.read_text()
    passed.append("Created sql_agent.py")

    # Modern patterns
    modern = ["ChatOpenAI", "create_react_agent", "@tool", "langgraph"]
    found = [p for p in modern if p in content]
    if found:
        passed.append(f"Modern: {', '.join(found)}")
    else:
        failed.append("No modern patterns")

    # Deprecated patterns
    deprecated = ["create_sql_agent", "LLMChain", "from langchain.llms"]
    found = [p for p in deprecated if p in content]
    if found:
        failed.append(f"Deprecated: {', '.join(found)}")
    else:
        passed.append("Avoided deprecated")

    # Check if CLAUDE.md was read (for context modes that have it)
    if did_read(events, "CLAUDE.md"):
        passed.append("Read CLAUDE.md")

    return passed, failed


def make_test_dir():
    test_dir = setup_test_environment()
    chinook = skills_root / "tests" / "langchain-agents" / "chinook.db"
    if chinook.exists():
        copy_test_data(chinook, test_dir)
    return test_dir


def run(model: str = None):
    print("CONTEXT IMPACT TEST\n")
    print("Comparing: none vs claude_md_only vs full context\n")

    results = run_comparison(
        name="SQL Agent",
        prompt=PROMPT,
        make_dir=make_test_dir,
        validate=validate,
        modes=[ContextMode.NONE, ContextMode.CLAUDE_MD_ONLY, ContextMode.FULL],
        model=model,
    )

    # Analysis
    print("\nANALYSIS:")
    none = results.get(ContextMode.NONE)
    with_md = results.get(ContextMode.CLAUDE_MD_ONLY)

    if none and with_md:
        diff = len(with_md.checks_passed) - len(none.checks_passed)
        if diff > 0:
            print(f"  CLAUDE.md improved by {diff} checks")
        elif diff < 0:
            print(f"  CLAUDE.md hurt by {-diff} checks")
        else:
            print(f"  No difference")

    return 0 if any(r.passed for r in results.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    sys.exit(run(model=args.model))
