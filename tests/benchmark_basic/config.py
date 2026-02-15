"""LangChain Agent experiment configuration.

Shared utilities for test_guidance.py, test_claudemd.py, and test_noise.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    MetricsCollector,
    OutputQualityValidator,
    PythonFileValidator,
    SkillInvokedValidator,
)
from skills.parser import load_skill

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"
agents_skill = load_skill(SKILL_BASE / "langchain_agents")

# Full sections from skill.md
FULL_SECTIONS = agents_skill["all"]


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
# GUIDANCE VARIATIONS (from original skill.py)
# =============================================================================
# Original skill.py had a GUIDANCE slot that could be POSITIVE, NEGATIVE, or None.
# We substitute this into the quick_start section along with tool overviews.
# =============================================================================

# Tool overviews (from skill.py CREATE_AGENT_OVERVIEW + DEEP_AGENT_OVERVIEW + LANGGRAPH_OVERVIEW)
_TOOL_OVERVIEWS = """**Simple tool-calling agent?** → [`create_agent`](https://docs.langchain.com/oss/python/langchain/agents)
```python
from langchain.agents import create_agent
graph = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search], system_prompt="...")
```
**Use this for:** Basic ReAct loops, tool-calling agents, simple Q&A bots.

**Need planning + filesystem + subagents?** → [`create_deep_agent`](https://docs.langchain.com/oss/python/deepagents/overview)
```python
from deepagents import create_deep_agent
agent = create_deep_agent(model=model, tools=tools, backend=FilesystemBackend())
```
**Use this for:** Research agents, complex workflows, multi-step planning.

**Custom control flow / multi-agent / advanced context?** → **LangGraph** (this guide)
**Use this for:** Custom routing logic, supervisor patterns, specialized state management, non-standard workflows.

**Start simple:** Build with basic ReAct loops first. Only add complexity (multi-agent, advanced context management) when your use case requires it."""

# POSITIVE: Only mentions what TO use (no deprecated pattern names)
GUIDANCE_POSITIVE = """**IMPORTANT:** Use modern LangChain patterns.

- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions

See the examples below for working code."""

# NEGATIVE: Mentions deprecated patterns (puts them in context)
GUIDANCE_NEGATIVE = """**IMPORTANT:** Use modern LangChain patterns.

Older helpers like `create_sql_agent`, `create_tool_calling_agent`, and the legacy `create_react_agent` are deprecated and should not be used.

- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions"""


def _build_quickstart(guidance):
    """Build quick_start section: guidance + tool overviews."""
    if guidance:
        return f"{guidance}\n\n{_TOOL_OVERVIEWS}"
    else:
        return _TOOL_OVERVIEWS


# Pre-built quick_start variants
QUICK_START_POSITIVE = _build_quickstart(GUIDANCE_POSITIVE)
QUICK_START_NEGATIVE = _build_quickstart(GUIDANCE_NEGATIVE)
QUICK_START_NEUTRAL = _build_quickstart(None)  # No guidance (for "_MOVED" variants)


def with_quickstart(content):
    """Return curated skill sections (matches old DEFAULT_SECTIONS).

    Excludes langgraph and resources for minimal content.
    """
    sections = agents_skill["sections"]
    return [
        sections["frontmatter"],
        sections["oneliner"],
        content if content else QUICK_START_NEUTRAL,
        sections["create_agent"],
    ]


def with_quickstart_all(content):
    """Return all skill sections including langgraph and resources.

    For ALL_SECTIONS treatment only.
    """
    sections = agents_skill["sections"]
    return [
        sections["frontmatter"],
        sections["oneliner"],
        content if content else QUICK_START_NEUTRAL,
        sections["create_agent"],
        sections["langgraph"],
        sections["resources"],
    ]


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
            "sql_agent_1.py",
            "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "sql_agent_1.py",
            "SQL Agent Output",
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
            "sql_agent_1.py",
            "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "sql_agent_1.py",
            "SQL Agent Output",
            task_description="SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold",
            expected_behavior="Should show genre names with track counts or sales numbers",
        ),
        PythonFileValidator(
            "search_agent.py",
            "Search Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        OutputQualityValidator(
            "search_agent.py",
            "Search Agent Output",
            task_description="Web search agent with mock search tool answering 'What is the capital of France?'",
            expected_behavior="Should return 'Paris' as the answer with proper agent reasoning",
        ),
        MetricsCollector(["sql_agent_1.py", "search_agent.py"]),
    ]


# =============================================================================
# ENVIRONMENT CONFIG
# =============================================================================

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt", "chinook.db"]
