"""LangChain Agent experiment.

Tests whether Claude uses modern patterns (create_agent, @tool) vs deprecated
patterns (create_sql_agent) when generating LangChain agents.
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
from skill_constructs.langchain.langchain_agents import (
    FRONTMATTER, HEADER, QUICK_START,
    CREATE_AGENT_OVERVIEW, DEEP_AGENT_OVERVIEW, LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE, SQL_EXAMPLE, QUICK_REFERENCE,
    GUIDANCE_POSITIVE, GUIDANCE_NEGATIVE,
    CLAUDE_MD_POSITIVE, CLAUDE_MD_NEGATIVE,
)

# =============================================================================
# SKILL SECTIONS
# =============================================================================

BASE_SECTIONS = [
    FRONTMATTER, HEADER, QUICK_START,
    None,  # <- GUIDANCE SLOT
    CREATE_AGENT_OVERVIEW, DEEP_AGENT_OVERVIEW, LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE, SQL_EXAMPLE, QUICK_REFERENCE,
]


def sections_with(guidance):
    result = BASE_SECTIONS.copy()
    result[3] = guidance
    return result


MINIMAL_SECTIONS = [
    FRONTMATTER, HEADER, QUICK_START, GUIDANCE_POSITIVE,
    CREATE_AGENT_OVERVIEW, None, None, None, None, QUICK_REFERENCE,
]

NO_SQL_SECTIONS = [
    FRONTMATTER, HEADER, QUICK_START, GUIDANCE_POSITIVE,
    CREATE_AGENT_OVERVIEW, DEEP_AGENT_OVERVIEW, LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE, None, QUICK_REFERENCE,
]


# =============================================================================
# PROMPTS
# =============================================================================

TASK1_PROMPT = """Build a SQL analytics agent for the chinook.db music store database.

Requirements:
1. Handle complex queries: multi-table JOINs, GROUP BY, date filtering, subqueries
2. Use gpt-4o-mini, only SELECT queries, include error handling
3. Test: "Which 3 genres generated the most revenue, and who are the top 2 artists in each?"

Save to sql_agent_1.py and run the test query."""

# Standard second task: another SQL agent
TASK2_SQL_PROMPT = """Build another SQL analytics agent for chinook.db with the same requirements.
Test: "What are the top 5 customers by total spending, and what genres do they prefer?"

Save to sql_agent_2.py and run the test query."""

# Alternative second task for noise tests: a web search agent (different domain)
TASK2_SEARCH_PROMPT = """Build a web search agent using the same modern patterns (create_agent, @tool).

Requirements:
1. Create a mock search tool that returns predefined results for queries
2. Agent should interpret user questions and call the search tool
3. Test with query: "What is the capital of France?"

Save to search_agent.py and run the test."""


# =============================================================================
# VALIDATORS
# =============================================================================

# Required patterns for SQL agent - ALL must be present
SQL_MODERN_PATTERNS = {
    "from langchain.agents import create_agent": "imports create_agent from langchain.agents",
    "create_agent(": "uses create_agent",
    "@tool": "@tool decorator",
}

# Deprecated patterns (none of these should be present)
SQL_FORBIDDEN = {
    "from langchain_community.agent_toolkits import create_sql_agent": "imports deprecated create_sql_agent toolkit",
    "from langchain.agents import create_sql_agent": "imports deprecated create_sql_agent",
    "from langgraph.prebuilt import create_react_agent": "imports deprecated create_react_agent",
    "create_react_agent(": "uses deprecated create_react_agent",
    "AgentExecutor(": "uses deprecated AgentExecutor",
    "initialize_agent(": "uses deprecated initialize_agent",
}

def sql_validators():
    """Standard validators for SQL agent treatments (both tasks are SQL)."""
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        # Agent 1: Code pattern check
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent 1 Code",
            required=SQL_MODERN_PATTERNS,
            forbidden=SQL_FORBIDDEN,
            require_all=True,
        ),
        # Agent 1: LLM-based output quality check
        OutputQualityValidator(
            "sql_agent_1.py", "SQL Agent 1 Output",
            task_description="SQL analytics agent querying chinook.db for top 3 genres by revenue and top 2 artists per genre",
            expected_behavior="Should show genre names (Rock, Latin, Metal, etc.), revenue amounts, and artist names with clear results",
        ),
        # Agent 2: Code pattern check
        PythonFileValidator(
            "sql_agent_2.py", "SQL Agent 2 Code",
            required=SQL_MODERN_PATTERNS,
            forbidden=SQL_FORBIDDEN,
            require_all=True,
        ),
        # Agent 2: LLM-based output quality check
        OutputQualityValidator(
            "sql_agent_2.py", "SQL Agent 2 Output",
            task_description="SQL analytics agent querying chinook.db for top 5 customers by spending and their genre preferences",
            expected_behavior="Should show customer names, total spending amounts, and preferred music genres",
        ),
        MetricsCollector(["sql_agent_1.py", "sql_agent_2.py"]),
    ]


def noise_validators():
    """Validators for noise treatments (SQL agent + search agent)."""
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        # SQL Agent: Code pattern check
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent Code",
            required=SQL_MODERN_PATTERNS,
            forbidden=SQL_FORBIDDEN,
            require_all=True,
        ),
        # SQL Agent: LLM-based output quality check
        OutputQualityValidator(
            "sql_agent_1.py", "SQL Agent Output",
            task_description="SQL analytics agent querying chinook.db for top 3 genres by revenue and top 2 artists per genre",
            expected_behavior="Should show genre names, revenue amounts, and artist names with clear results",
        ),
        # Search Agent: Code pattern check
        PythonFileValidator(
            "search_agent.py", "Search Agent Code",
            required=SQL_MODERN_PATTERNS,
            forbidden=SQL_FORBIDDEN,
            require_all=True,
        ),
        # Search Agent: LLM-based output quality check
        OutputQualityValidator(
            "search_agent.py", "Search Agent Output",
            task_description="Web search agent with mock search tool answering 'What is the capital of France?'",
            expected_behavior="Should return 'Paris' as the answer with proper agent reasoning",
        ),
        MetricsCollector(["sql_agent_1.py", "search_agent.py"]),
    ]


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Control
    "CONTROL": Treatment(
        description="No skill (control)",
        validators=sql_validators(),
    ),
    "BASELINE": Treatment(
        description="Skill with positive guidance",
        sections=sections_with(GUIDANCE_POSITIVE),
        validators=sql_validators(),
    ),

    # Guidance framing
    "GUIDANCE_POS": Treatment(
        description="Positive guidance only",
        sections=sections_with(GUIDANCE_POSITIVE),
        validators=sql_validators(),
    ),
    "GUIDANCE_NEG": Treatment(
        description="Negative guidance (mentions deprecated)",
        sections=sections_with(GUIDANCE_NEGATIVE),
        validators=sql_validators(),
    ),

    # CLAUDE.md
    "CLAUDE_MD_POS": Treatment(
        description="Skill + CLAUDE.md positive",
        sections=sections_with(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_POSITIVE,
        validators=sql_validators(),
    ),
    "CLAUDE_MD_NEG": Treatment(
        description="Skill + CLAUDE.md negative",
        sections=sections_with(GUIDANCE_NEGATIVE),
        claude_md=CLAUDE_MD_NEGATIVE,
        validators=sql_validators(),
    ),
    "CLAUDE_MD_MOVED": Treatment(
        description="Guidance in CLAUDE.md only",
        sections=sections_with(None),
        claude_md=CLAUDE_MD_POSITIVE,
        validators=sql_validators(),
    ),

    # Noise (progressive: 1, 2, 3 noise tasks) - uses search agent as 2nd task
    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        sections=sections_with(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns"],
        validators=noise_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        sections=sections_with(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components"],
        validators=noise_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        sections=sections_with(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components", "api-docs"],
        validators=noise_validators(),
    ),

    # Noise + treatments
    "NOISE_NEG": Treatment(
        description="Noise + negative guidance",
        sections=sections_with(GUIDANCE_NEGATIVE),
        noise_tasks=["docker-patterns"],
        validators=noise_validators(),
    ),
    "NOISE_CLAUDE_MD": Treatment(
        description="Noise + CLAUDE.md",
        sections=sections_with(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_POSITIVE,
        noise_tasks=["docker-patterns"],
        validators=sql_validators(),
    ),

    # Minimal (stress tests)
    "MINIMAL": Treatment(
        description="Minimal documentation",
        sections=MINIMAL_SECTIONS,
        validators=sql_validators(),
    ),
    "MINIMAL_NOISE": Treatment(
        description="Minimal + noise",
        sections=MINIMAL_SECTIONS,
        noise_tasks=["docker-patterns"],
        validators=sql_validators(),
    ),
    "NO_SQL_EXAMPLE": Treatment(
        description="No SQL example",
        sections=NO_SQL_SECTIONS,
        validators=sql_validators(),
    ),
}


# Noise treatments that should use search agent as second task
NOISE_TREATMENTS = {"NOISE_1", "NOISE_2", "NOISE_3", "NOISE_NEG", "NOISE_CLAUDE_MD", "MINIMAL_NOISE"}


def build_sql_prompt(treatment: Treatment, treatment_name: str = None) -> str:
    """Build the prompt for a SQL treatment.

    For noise treatments, uses search agent as second task to test
    if Claude can apply patterns across different domains.
    """
    if treatment_name and treatment_name in NOISE_TREATMENTS:
        return treatment.build_prompt(TASK1_PROMPT, TASK2_SEARCH_PROMPT)
    return treatment.build_prompt(TASK1_PROMPT, TASK2_SQL_PROMPT)


def validate_sql_treatment(events: dict, test_dir: Path, treatment: Treatment):
    """Validate a SQL treatment."""
    return treatment.validate(events, test_dir)


# Presets
CONTROL_COMPARISON = ["CONTROL", "BASELINE"]
GUIDANCE_COMPARISON = ["GUIDANCE_POS", "GUIDANCE_NEG"]
CLAUDE_MD_COMPARISON = ["BASELINE", "CLAUDE_MD_POS", "CLAUDE_MD_MOVED"]
NOISE_COMPARISON = ["BASELINE", "NOISE_1", "NOISE_2", "NOISE_3"]
NOISE_TREATMENT_COMPARISON = ["NOISE_1", "NOISE_NEG", "NOISE_CLAUDE_MD"]
MINIMAL_COMPARISON = ["BASELINE", "MINIMAL", "NO_SQL_EXAMPLE"]
STRESS_COMPARISON = ["MINIMAL", "MINIMAL_NOISE"]
ALL_TREATMENTS = list(TREATMENTS.keys())
