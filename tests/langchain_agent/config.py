"""LangChain Agent experiment configuration.

Shared utilities for test_guidance.py, test_claudemd.py, and test_noise.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    Treatment,
    SkillInvokedValidator,
    PythonFileValidator,
    MetricsCollector,
    OutputQualityValidator,
)
from skill_constructs.parser import load_skill
from skill_constructs import CLAUDE_SAMPLE

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skill_constructs" / "langchain"
agents_skill = load_skill(SKILL_BASE / "langchain_agents")

# Full sections from skill.md
FULL_SECTIONS = agents_skill["all"]


# =============================================================================
# EXPERIMENT-SPECIFIC GUIDANCE
# =============================================================================

GUIDANCE_POSITIVE = """**DO use these patterns:**
- `from langchain.agents import create_agent` - The modern way to build agents
- `@tool` decorator - Modern tool definition
- LangGraph for complex control flow

These are the current best practices for LangChain agents."""

GUIDANCE_NEGATIVE = """**DON'T use these deprecated patterns:**
- `create_sql_agent` from langchain_community - Deprecated
- `create_react_agent` from langgraph.prebuilt - Outdated
- `AgentExecutor` - Legacy pattern
- `initialize_agent` - Deprecated

Use `create_agent` from `langchain.agents` instead."""


# =============================================================================
# CLAUDE.MD VARIANTS
# =============================================================================

CLAUDE_MD_SKILLS_ONLY = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
"""

CLAUDE_MD_SKILLS_REQUIRED = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
**Always use skills when they are available for your task.**
"""

CLAUDE_MD_PATTERNS_POSITIVE = """# Project Guidelines

## LangChain Best Practices
When building LangChain agents:
- Use `create_agent` from `langchain.agents` (modern approach)
- Use `@tool` decorator for tool definitions
- Use LangGraph for complex control flow
"""

CLAUDE_MD_BOTH = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.

## LangChain Best Practices
When building LangChain agents:
- Use `create_agent` from `langchain.agents` (modern approach)
- Use `@tool` decorator for tool definitions
- Use LangGraph for complex control flow
"""


# =============================================================================
# SKILL SECTION BUILDERS
# =============================================================================

def sections_with_guidance(guidance):
    """Build skill sections list with guidance inserted after quick_start."""
    sections = agents_skill["sections"]
    base = [
        sections["frontmatter"],
        sections["oneliner"],
        sections["quick_start"],
    ]
    if guidance:
        base.append(guidance)
    base.extend([
        sections["create_agent"],
        sections["langgraph"],
        sections["resources"],
    ])
    return base


# =============================================================================
# PROMPTS
# =============================================================================

TASK1_PROMPT = """Build a SQL analytics agent for the chinook.db music store database.

Requirements:
1. Handle queries with JOINs and GROUP BY
2. Use gpt-4o-mini, only SELECT queries, include error handling
3. Test: "What are the top 5 best-selling genres by total tracks sold?"

Save to sql_agent_1.py and run the test query.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""

TASK2_SEARCH_PROMPT = """Build a web search agent using the same modern LangChain patterns.

Requirements:
1. Create a mock search tool that returns predefined results for queries
2. Agent should interpret user questions and call the search tool
3. Test with query: "What is the capital of France?"

Save to search_agent.py and run the test.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""


# =============================================================================
# VALIDATORS
# =============================================================================

# Required modern patterns - ALL must be present
AGENT_MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "create_agent(": "uses create_agent",
    "@tool": "@tool decorator",
}

# Deprecated patterns (none of these should be present)
AGENT_FORBIDDEN = {
    "from langchain_community.agent_toolkits import create_sql_agent": "imports deprecated create_sql_agent toolkit",
    "from langgraph.prebuilt import create_react_agent": "imports deprecated create_react_agent",
    "create_react_agent(": "uses deprecated create_react_agent",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
}


def sql_agent_validators():
    """Validators for single SQL agent task."""
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "sql_agent_1.py", "SQL Agent Output",
            task_description="SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold",
            expected_behavior="Should show genre names (Rock, Latin, Metal, etc.) with track counts or sales numbers",
        ),
        MetricsCollector(["sql_agent_1.py"]),
    ]


def noise_validators():
    """Validators for noise treatments (SQL agent + search agent)."""
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "sql_agent_1.py", "SQL Agent Output",
            task_description="SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold",
            expected_behavior="Should show genre names with track counts or sales numbers",
        ),
        PythonFileValidator(
            "search_agent.py", "Search Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "search_agent.py", "Search Agent Output",
            task_description="Web search agent with mock search tool answering 'What is the capital of France?'",
            expected_behavior="Should return 'Paris' as the answer with proper agent reasoning",
        ),
        MetricsCollector(["sql_agent_1.py", "search_agent.py"]),
    ]
