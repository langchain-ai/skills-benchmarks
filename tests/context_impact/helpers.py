"""Shared test helpers for context impact tests."""

from pathlib import Path

# Shared across all context impact tests
PROMPT = """Build a LangChain SQL agent that can query chinook.db.
Requirements: Use gpt-4o-mini, only allow SELECT queries, include error handling.
Save to sql_agent.py and run a test query."""

CHINOOK_PATH = Path(__file__).parent / "chinook.db"


def validate_sql_agent(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Validate SQL agent output.

    Pass criteria: Used modern patterns AND avoided deprecated create_sql_agent

    Note: Skills are loaded via Claude Code's memory system, not Read tool,
    so we validate based on code patterns, not file reads.
    """
    passed, failed = [], []
    agent_file = test_dir / "sql_agent.py"

    if not agent_file.exists():
        return passed, ["sql_agent.py not created"]

    content = agent_file.read_text()
    passed.append("Created file")

    # Check for modern patterns (what skill recommends)
    if "create_agent(" in content:
        passed.append("Uses create_agent")
    if "@tool" in content:
        passed.append("Uses @tool")
    if "langgraph" in content.lower() or "create_react_agent" in content:
        passed.append("Uses LangGraph")

    # Check for deprecated IMPORT (not just function name Claude chose)
    # The deprecated pattern is: from langchain... import create_sql_agent
    import_lines = [line for line in content.split('\n') if line.strip().startswith(('from ', 'import '))]
    for line in import_lines:
        if 'create_sql_agent' in line:
            failed.append("Imports create_sql_agent (deprecated)")

    return passed, failed


def make_test_dir(case_name: str) -> Path:
    """Create test directory for a case."""
    from scaffold.setup import setup_test_environment, copy_test_data
    from scaffold.templates import setup_test_context
    from tests.context_impact.cases import CASES

    desc, claude_md, sections = CASES[case_name]
    test_dir = setup_test_environment()
    setup_test_context(test_dir, sections=sections, claude_md=claude_md)

    if CHINOOK_PATH.exists():
        copy_test_data(CHINOOK_PATH, test_dir)

    return test_dir
