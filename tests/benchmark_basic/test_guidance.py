"""Guidance treatments (positive vs negative framing in skills).

Tests whether framing matters: "DO use modern patterns" vs "DON'T use deprecated".

Run with: pytest tests/benchmark_basic/test_guidance.py -v
Parallel:  pytest tests/benchmark_basic/test_guidance.py -n 3
"""

from pathlib import Path

import pytest

from scaffold import (
    MetricsCollector,
    OutputQualityValidator,
    PythonFileValidator,
    SkillInvokedValidator,
    Treatment,
)
from scaffold.python import extract_events, parse_output
from skills.parser import load_skill

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"
agents_skill = load_skill(SKILL_BASE / "langchain_basic")

# =============================================================================
# CONSTANTS
# =============================================================================

ENVIRONMENT_DIR = Path(__file__).parent / "environment"

CLAUDE_MD_SKILLS_REQUIRED = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
**Always use skills when they are available for your task.**
"""

TASK1_PROMPT = """Build a SQL analytics agent for the chinook.db music store database.

Requirements:
1. Handle queries with JOINs and GROUP BY
2. Use gpt-4o-mini, only SELECT queries, include error handling
3. Test: "What are the top 5 best-selling genres by total tracks sold?"

Save to sql_agent_1.py and run the test query.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""

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


QUICK_START_POSITIVE = _build_quickstart(GUIDANCE_POSITIVE)
QUICK_START_NEGATIVE = _build_quickstart(GUIDANCE_NEGATIVE)


def with_quickstart(content):
    """Return curated skill sections (matches old DEFAULT_SECTIONS).

    Excludes langgraph and resources for minimal content.
    """
    sections = agents_skill["sections"]
    quickstart_content = content if content else _build_quickstart(None)
    return [
        sections["frontmatter"],
        sections["oneliner"],
        f"<quick_start>\n{quickstart_content}\n</quick_start>",
        sections["create_agent"],
    ]


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


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    "GUIDANCE_POS": Treatment(
        description="Skill with positive guidance (DO use modern patterns)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),
    "GUIDANCE_NEG": Treatment(
        description="Skill with negative guidance (DON'T use deprecated)",
        skills={"langchain-agents": with_quickstart(QUICK_START_NEGATIVE)},
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),
}


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def environment_dir():
    """Path to environment directory with Dockerfile, requirements.txt, etc."""
    return ENVIRONMENT_DIR


# =============================================================================
# TESTS
# =============================================================================


@pytest.mark.parametrize("treatment_name", list(TREATMENTS.keys()))
def test_treatment(
    treatment_name,
    verify_environment,
    test_dir,
    setup_test_context,
    run_claude,
    record_result,
    environment_dir,
):
    """Test a single treatment."""
    treatment = TREATMENTS[treatment_name]

    # Setup test context
    setup_test_context(
        skills=treatment.skills,
        claude_md=treatment.claude_md,
        environment_dir=environment_dir,
    )

    # Build prompt
    prompt = treatment.build_prompt(TASK1_PROMPT)

    # Run Claude (automatically saves raw output)
    result = run_claude(prompt, timeout=600)

    # Parse output
    events = extract_events(parse_output(result.stdout))

    # Validate
    passed, failed = treatment.validate(events, test_dir, {})

    # Record results (saves events, artifacts, reports)
    record_result(events, passed, failed)

    # Assert
    assert not failed, f"Validation failed: {failed}"
