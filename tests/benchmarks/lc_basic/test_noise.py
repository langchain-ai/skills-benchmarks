"""Noise treatments (effects of distractor tasks on skill retention).

Tests skill retention when distracted by unrelated tasks.

Run with: pytest tests/benchmarks/lc_basic/test_noise.py -v
Parallel:  pytest tests/benchmarks/lc_basic/test_noise.py -n 3
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

from ..helpers import get_noise_skills, get_noise_tasks

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent.parent / "skills" / "benchmarks"
agents_skill = load_skill(SKILL_BASE / "langchain_basic")

# Build skill sections with positive guidance
_sections = agents_skill["sections"]
SKILL_SECTIONS = [
    _sections["frontmatter"],
    _sections["oneliner"],
    """<quick_start>
**IMPORTANT:** Use modern LangChain patterns.

- `create_agent()` from `langchain.agents` for simple agents
- LangGraph `create_react_agent` for complex flows
- `@tool` decorator for tool definitions

See the examples below for working code.

**Simple tool-calling agent?** → [`create_agent`](https://docs.langchain.com/oss/python/langchain/agents)
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

**Start simple:** Build with basic ReAct loops first. Only add complexity (multi-agent, advanced context management) when your use case requires it.
</quick_start>""",
    _sections["create_agent"],
]

# =============================================================================
# CONSTANTS
# =============================================================================

ENVIRONMENT_DIR = Path(__file__).parent / "environment"

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
# TREATMENTS
# =============================================================================


def build_skills(noise_task_names: list[str] = None) -> dict[str, list[str]]:
    """Build skills dict with langchain-agents plus any noise skills.

    Always includes langchain-agents as the primary skill.
    Noise skills are added for distractor task treatments.
    """
    skills = {"langchain-agents": SKILL_SECTIONS}  # Always include main skill
    if noise_task_names:
        skills.update(get_noise_skills(noise_task_names))
    return skills


TREATMENTS = {
    "NOISE_BASELINE": Treatment(
        description="Baseline for noise comparison (no noise)",
        skills=build_skills(),  # langchain-agents only
        validators=noise_validators(),
    ),
    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        skills=build_skills(["docker-patterns"]),  # langchain-agents + docker
        noise_tasks=get_noise_tasks(["docker-patterns"]),
        validators=noise_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        skills=build_skills(
            ["docker-patterns", "react-components"]
        ),  # langchain-agents + docker + react
        noise_tasks=get_noise_tasks(["docker-patterns", "react-components"]),
        validators=noise_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        skills=build_skills(
            ["docker-patterns", "react-components", "api-docs"]
        ),  # langchain-agents + all noise
        noise_tasks=get_noise_tasks(["docker-patterns", "react-components", "api-docs"]),
        validators=noise_validators(),
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

    # Build prompt (noise treatments use two task prompts)
    prompt = treatment.build_prompt(TASK1_PROMPT, TASK2_SEARCH_PROMPT)

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
