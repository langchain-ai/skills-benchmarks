"""Test case definitions for CLAUDE.md impact testing.

SKILL SECTIONS (from skill_constructs/langchain/langchain_agents/skill.py):
  [0] FRONTMATTER        - Skill metadata
  [1] HEADER             - Title and intro
  [2] QUICK_START        - "Which tool?" section header
  [3] GUIDANCE           - *** SUBSTITUTED IN TESTS ***
  [4] CREATE_AGENT_OVERVIEW
  [5] DEEP_AGENT_OVERVIEW
  [6] LANGGRAPH_OVERVIEW
  [7] CREATE_AGENT_EXAMPLE
  [8] SQL_EXAMPLE
  [9] QUICK_REFERENCE
"""

import ast
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold.logs import did_invoke_skill

from skill_constructs.langchain.langchain_agents import (
    FRONTMATTER, HEADER, QUICK_START, GUIDANCE,
    CREATE_AGENT_OVERVIEW, DEEP_AGENT_OVERVIEW, LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE, SQL_EXAMPLE, QUICK_REFERENCE,
)

# =============================================================================
# GUIDANCE VARIATIONS (substitute at index 3)
# =============================================================================

# NEGATIVE: Mentions deprecated patterns (puts create_sql_agent in context)
GUIDANCE_NEGATIVE = """## Important: Use Modern LangChain Patterns

Older helpers like `create_sql_agent`, `create_tool_calling_agent`, and the legacy `create_react_agent` are deprecated and should not be used.

Use the modern approach:
- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions"""

# POSITIVE: Only mentions what TO use (no deprecated pattern names)
GUIDANCE_POSITIVE = """## Important: Use Modern LangChain Patterns

Use the modern approach:
- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions

See the examples below for working code."""

# =============================================================================
# CLAUDE.MD VARIATIONS
# =============================================================================

# NEGATIVE: Mentions deprecated patterns (general principle)
CLAUDE_MD_NEGATIVE = """# Project Guidelines

Always check project skills before starting a task to ensure you're using the recommended patterns.

## LangChain Development

Use modern LangChain patterns. Older convenience helpers are deprecated and should be avoided.
"""

# POSITIVE: Only mentions what TO use (general principle)
CLAUDE_MD_POSITIVE = """# Project Guidelines

Always check project skills before starting a task to ensure you're using the recommended patterns.

## LangChain Development

Use modern LangChain patterns.
"""

# =============================================================================
# SECTION ASSEMBLY
# =============================================================================

BASE_SECTIONS = [
    FRONTMATTER,            # [0]
    HEADER,                 # [1]
    QUICK_START,            # [2]
    None,                   # [3] <- GUIDANCE SLOT
    CREATE_AGENT_OVERVIEW,  # [4]
    DEEP_AGENT_OVERVIEW,    # [5]
    LANGGRAPH_OVERVIEW,     # [6]
    CREATE_AGENT_EXAMPLE,   # [7]
    SQL_EXAMPLE,            # [8]
    QUICK_REFERENCE,        # [9]
]


def sections_with(guidance: Optional[str]) -> List[str]:
    """Return section list with specified guidance at index 3."""
    result = BASE_SECTIONS.copy()
    result[3] = guidance
    return result


# =============================================================================
# TEST CASES
# Format: (description, claude_md, sections)
#
# Hypothesis: Negative framing puts deprecated patterns in context, making
# Claude more likely to use them even when told not to.
# =============================================================================

CASES = {
    # --- BASELINE: Skill with negative guidance (mentions deprecated) ---
    "SKILL_NEG": (
        "Skill only, negative guidance",
        None,
        sections_with(GUIDANCE_NEGATIVE),
    ),

    # --- SKILL_POS: Skill with positive guidance only ---
    "SKILL_POS": (
        "Skill only, positive guidance",
        None,
        sections_with(GUIDANCE_POSITIVE),
    ),

    # --- SKILL_NONE: Skill with no guidance section ---
    "SKILL_NONE": (
        "Skill only, no guidance",
        None,
        sections_with(None),
    ),

    # --- REITERATE: Both skill and CLAUDE.md have same guidance ---
    "REITERATE_NEG": (
        "Skill + CLAUDE.md, both negative",
        CLAUDE_MD_NEGATIVE,
        sections_with(GUIDANCE_NEGATIVE),
    ),

    "REITERATE_POS": (
        "Skill + CLAUDE.md, both positive",
        CLAUDE_MD_POSITIVE,
        sections_with(GUIDANCE_POSITIVE),
    ),

    # --- MOVED: Guidance removed from skill, placed in CLAUDE.md ---
    "MOVED_NEG": (
        "Guidance moved to CLAUDE.md (negative)",
        CLAUDE_MD_NEGATIVE,  # Same content as GUIDANCE_NEGATIVE
        sections_with(None),  # Guidance removed from skill
    ),

    "MOVED_POS": (
        "Guidance moved to CLAUDE.md (positive)",
        CLAUDE_MD_POSITIVE,
        sections_with(None),
    ),
}

# =============================================================================
# CASE GROUPS FOR COMPARISON
# =============================================================================

# Compare negative vs positive framing
FRAMING_COMPARISON = ["SKILL_NEG", "SKILL_POS"]

# Compare guidance location (skill vs CLAUDE.md)
LOCATION_COMPARISON = ["SKILL_NEG", "MOVED_NEG"]

# Compare reiteration effect
REITERATION_COMPARISON = ["SKILL_NEG", "REITERATE_NEG"]

# Full positive strategy comparison
POSITIVE_STRATEGY = ["SKILL_POS", "REITERATE_POS", "MOVED_POS"]

# Full negative strategy comparison
NEGATIVE_STRATEGY = ["SKILL_NEG", "REITERATE_NEG", "MOVED_NEG"]


# =============================================================================
# HARDER TEST CASES - Minimal skill documentation
# =============================================================================

# Minimal: Only header + quick_start + quick reference (no detailed examples)
MINIMAL_SECTIONS = [
    FRONTMATTER,
    HEADER,
    QUICK_START,
    GUIDANCE_POSITIVE,  # Use positive guidance
    CREATE_AGENT_OVERVIEW,  # Just the overview, not the detailed example
    None,  # No deep agent
    None,  # No langgraph
    None,  # No create_agent example
    None,  # No SQL example
    QUICK_REFERENCE,
]

# No SQL example: Has general examples but Claude must apply to SQL task
NO_SQL_SECTIONS = [
    FRONTMATTER,
    HEADER,
    QUICK_START,
    GUIDANCE_POSITIVE,
    CREATE_AGENT_OVERVIEW,
    DEEP_AGENT_OVERVIEW,
    LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE,  # General example only
    None,  # No SQL example - Claude must figure it out
    QUICK_REFERENCE,
]

CASES.update({
    # --- HARDER: Minimal documentation ---
    "MINIMAL": (
        "Minimal skill - overview + quick ref only",
        None,
        MINIMAL_SECTIONS,
    ),

    "NO_SQL_EXAMPLE": (
        "No SQL example - general patterns only",
        None,
        NO_SQL_SECTIONS,
    ),

    # --- MINIMAL + CLAUDE.md combinations ---
    "MINIMAL_REITERATE": (
        "Minimal skill + CLAUDE.md positive guidance",
        CLAUDE_MD_POSITIVE,
        MINIMAL_SECTIONS,
    ),

    "MINIMAL_MOVED": (
        "Minimal skill (no guidance) + CLAUDE.md guidance",
        CLAUDE_MD_POSITIVE,
        [FRONTMATTER, HEADER, QUICK_START, None, CREATE_AGENT_OVERVIEW,
         None, None, None, None, QUICK_REFERENCE],  # Same as MINIMAL but no guidance
    ),

    "NO_SQL_REITERATE": (
        "No SQL example + CLAUDE.md positive guidance",
        CLAUDE_MD_POSITIVE,
        NO_SQL_SECTIONS,
    ),
})

# Difficulty comparison
DIFFICULTY_COMPARISON = ["SKILL_POS", "NO_SQL_EXAMPLE", "MINIMAL"]

# Test if CLAUDE.md helps with minimal skills
MINIMAL_BOOST_COMPARISON = ["MINIMAL", "MINIMAL_REITERATE", "MINIMAL_MOVED"]
NO_SQL_BOOST_COMPARISON = ["NO_SQL_EXAMPLE", "NO_SQL_REITERATE"]


# =============================================================================
# VALIDATORS
# =============================================================================

def verify_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if Python file has valid syntax."""
    try:
        ast.parse(file_path.read_text())
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def validate_sql_agent(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Validate SQL agent output.

    Pass criteria:
    1. langchain-agents skill was invoked
    2. Used modern patterns AND avoided deprecated create_sql_agent
    3. Generated code has valid syntax
    4. Generated agent runs without import errors

    Also tracks efficiency metrics (turns, deprecated attempts).
    """
    passed, failed = [], []
    agent_file = test_dir / "sql_agent.py"

    # Track efficiency metrics
    num_turns = events.get("num_turns", 0)
    duration = events.get("duration_seconds", 0)

    # Count deprecated pattern attempts in tool calls
    deprecated_attempts = count_deprecated_attempts(events)

    # 1. Check skill invocation
    if did_invoke_skill(events, "langchain-agents"):
        passed.append("Invoked langchain-agents skill")
    else:
        failed.append("Did NOT invoke langchain-agents skill")

    # 2. Check file created
    if not agent_file.exists():
        failed.append("sql_agent.py not created")
        return passed, failed

    content = agent_file.read_text()
    passed.append("Created file")

    # 3. Check for modern patterns (what skill recommends)
    # ONLY create_agent and create_deep_agent are modern - NOT create_react_agent
    if "create_agent(" in content:
        passed.append("Uses create_agent")
    if "create_deep_agent(" in content:
        passed.append("Uses create_deep_agent")
    if "@tool" in content:
        passed.append("Uses @tool")

    # 4. Check for deprecated IMPORT (not just function name Claude chose)
    import_lines = [line for line in content.split('\n') if line.strip().startswith(('from ', 'import '))]
    for line in import_lines:
        if 'create_sql_agent' in line:
            failed.append("Imports create_sql_agent (deprecated)")

    # 5. Verify code is syntactically valid
    syntax_ok, syntax_err = verify_syntax(agent_file)
    if syntax_ok:
        passed.append("Valid syntax")
    else:
        failed.append(f"Syntax error: {syntax_err}")
        return passed, failed  # Can't run if syntax is invalid

    # 6. Verify code runs (imports work, no runtime errors on load)
    runs_ok, run_err = verify_agent_runs(test_dir, agent_file)
    if runs_ok:
        passed.append("Agent runs")
    else:
        failed.append(f"Runtime error: {run_err}")

    # 7. Add efficiency metrics as info (not pass/fail)
    passed.append(f"Turns: {num_turns}")
    passed.append(f"Duration: {duration:.0f}s")
    if deprecated_attempts > 0:
        passed.append(f"Deprecated attempts: {deprecated_attempts}")

    return passed, failed


def count_deprecated_attempts(events: dict) -> int:
    """Count how many times deprecated patterns appeared in Write/Edit tool calls."""
    deprecated_patterns = [
        "create_sql_agent", "create_tool_calling_agent",
        "create_react_agent", "AgentExecutor"
    ]
    count = 0
    for tc in events.get("tool_calls", []):
        if tc.get("tool") in ("Write", "Edit"):
            content = tc.get("input", {}).get("content", "") or tc.get("input", {}).get("new_string", "")
            for pattern in deprecated_patterns:
                if pattern in content:
                    count += 1
                    break  # Only count once per tool call
    return count


def verify_agent_runs(test_dir: Path, agent_file: Path) -> tuple[bool, str]:
    """Verify the agent file actually runs.

    Runs the file with python, inheriting current environment variables
    (including OPENAI_API_KEY etc). The file should have a main block
    that runs a test query.
    """
    # Check if venv exists (Claude often creates one)
    venv_python = test_dir / "venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = sys.executable

    # Inherit current environment (includes API keys)
    env = os.environ.copy()

    try:
        result = subprocess.run(
            [python_cmd, str(agent_file)],
            capture_output=True,
            text=True,
            timeout=120,  # Give time for API calls
            cwd=str(test_dir),
            env=env,
        )
        # Check for success - either exit 0 or output that looks like it worked
        if result.returncode == 0:
            return True, ""
        else:
            error = result.stderr.strip() or result.stdout.strip()
            # Truncate long errors
            if len(error) > 300:
                error = error[:300] + "..."
            return False, error
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (120s)"
    except Exception as e:
        return False, str(e)
