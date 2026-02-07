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

import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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

# NEGATIVE: Mentions deprecated patterns
CLAUDE_MD_NEGATIVE = """# Project Guidelines

Always check project skills before starting a task to ensure you're using the recommended patterns.

## LangChain Development

Older helpers like `create_sql_agent` and `create_tool_calling_agent` are deprecated. Use these instead:
- `create_agent()` from `langchain.agents`
- LangGraph for complex agent flows
- `@tool` decorator for tool definitions
"""

# POSITIVE: Only mentions what TO use
CLAUDE_MD_POSITIVE = """# Project Guidelines

Always check project skills before starting a task to ensure you're using the recommended patterns.

## LangChain Development

Use these patterns:
- `create_agent()` from `langchain.agents`
- LangGraph for complex agent flows
- `@tool` decorator for tool definitions
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
