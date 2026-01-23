#!/usr/bin/env python3
"""
Baseline test for SQL agent creation - NO context provided.

Tests raw Claude Code capability without CLAUDE.md or skill documentation.
"""

import sys
import argparse
from pathlib import Path

skills_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_root))

from scaffold.setup import setup_test_environment, cleanup_test_environment, copy_test_data
from scaffold.runner import run_test, ContextMode


PROMPT = """Build a Python text-to-SQL agent using LangChain that can query the chinook.db SQLite database.

Requirements:
- Use gpt-4o-mini model
- Only allow SELECT queries
- Include error handling

Save to sql_agent.py and run a test query."""


def validate(trace: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Validate based on trace and generated files."""
    passed, failed = [], []

    # Check file was created
    agent_file = test_dir / "sql_agent.py"
    if agent_file.exists():
        passed.append("Created sql_agent.py")
        content = agent_file.read_text()

        # Check for modern patterns
        modern = ["ChatOpenAI", "create_react_agent", "@tool", "langgraph"]
        found_modern = [p for p in modern if p in content]
        if found_modern:
            passed.append(f"Modern patterns: {', '.join(found_modern)}")
        else:
            failed.append("No modern patterns found")

        # Check for deprecated patterns
        deprecated = ["create_sql_agent", "LLMChain", "from langchain.llms"]
        found_deprecated = [p for p in deprecated if p in content]
        if found_deprecated:
            failed.append(f"Deprecated patterns: {', '.join(found_deprecated)}")
        else:
            passed.append("Avoided deprecated patterns")
    else:
        failed.append("sql_agent.py not created")

    return passed, failed


def run(model: str = None):
    test_dir = setup_test_environment()

    # Copy test database
    chinook_db = skills_root / "tests" / "langchain-agents" / "chinook.db"
    if chinook_db.exists():
        copy_test_data(chinook_db, test_dir)

    result = run_test(
        name="Baseline: SQL Agent",
        prompt=PROMPT,
        test_dir=test_dir,
        validate=validate,
        model=model,
        context=ContextMode.NONE,
    )

    cleanup_test_environment(test_dir)
    return 0 if result.passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    return run(model=args.model)


if __name__ == "__main__":
    sys.exit(main())
