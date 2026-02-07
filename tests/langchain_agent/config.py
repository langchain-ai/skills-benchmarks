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
    CREATE_AGENT_EXAMPLE, TOOL_EXAMPLE, QUICK_REFERENCE,
    GUIDANCE_POSITIVE, GUIDANCE_NEGATIVE,
    CLAUDE_MD_SKILLS_ONLY, CLAUDE_MD_SKILLS_REQUIRED, CLAUDE_MD_PATTERNS_POSITIVE, CLAUDE_MD_BOTH,
    FULL_SECTIONS,
)
from skill_constructs import CLAUDE_SAMPLE

# =============================================================================
# SKILL SECTIONS
# =============================================================================

BASE_SECTIONS = [
    FRONTMATTER, HEADER, QUICK_START,
    None,  # <- GUIDANCE SLOT
    CREATE_AGENT_OVERVIEW, DEEP_AGENT_OVERVIEW, LANGGRAPH_OVERVIEW,
    CREATE_AGENT_EXAMPLE, TOOL_EXAMPLE, QUICK_REFERENCE,
]


def sections_guidance(guidance):
    """Build sections list with guidance inserted."""
    result = BASE_SECTIONS.copy()
    result[3] = guidance
    return result


def skill(guidance):
    """Build skills dict with langchain-agents skill."""
    return {"langchain-agents": sections_guidance(guidance)}




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

# Standard second task: another SQL agent
TASK2_SQL_PROMPT = """Build another SQL analytics agent for chinook.db with the same requirements.
Test: "What are the top 5 customers by total spending, and what genres do they prefer?"

Save to sql_agent_2.py and run the test query.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""

# Alternative second task for noise tests: a web search agent (different domain)
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
        # SQL Agent: Code pattern check
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        # SQL Agent: LLM-based output quality check
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
        # SQL Agent: Code pattern check
        PythonFileValidator(
            "sql_agent_1.py", "SQL Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
            require_all=True,
        ),
        # SQL Agent: LLM-based output quality check
        OutputQualityValidator(
            "sql_agent_1.py", "SQL Agent Output",
            task_description="SQL analytics agent querying chinook.db for top 5 best-selling genres by tracks sold",
            expected_behavior="Should show genre names with track counts or sales numbers",
        ),
        # Search Agent: Code pattern check
        PythonFileValidator(
            "search_agent.py", "Search Agent Code",
            required=AGENT_MODERN_PATTERNS,
            forbidden=AGENT_FORBIDDEN,
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
# Organized into 3 experiment classes:
#   1. REINFORCEMENT: Effects of positive vs negative guidance in skills
#   2. CLAUDE_MD: Effects of CLAUDE.md presence and content
#   3. NOISE: Effects of distractor tasks on skill retention
# =============================================================================

TREATMENTS = {
    # =========================================================================
    # CLASS 1: REINFORCEMENT - Positive vs Negative Guidance in Skills
    # =========================================================================
    # Tests whether framing matters (DO use X vs DON'T use Y)

    "GUIDANCE_POS": Treatment(
        description="Skill with positive guidance (DO use modern patterns)",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),
    "GUIDANCE_NEG": Treatment(
        description="Skill with negative guidance (DON'T use deprecated)",
        skills=skill(GUIDANCE_NEGATIVE),
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),

    # =========================================================================
    # CLASS 2: CLAUDE_MD - Effects of CLAUDE.md Presence and Content
    # =========================================================================
    # Tests whether CLAUDE.md is needed and what instructions work best

    # Baselines (no CLAUDE.md)
    "CONTROL": Treatment(
        description="No skill, no CLAUDE.md (pure control)",
        validators=sql_agent_validators(),
    ),
    "ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={"langchain-agents": FULL_SECTIONS},
        claude_md=CLAUDE_SAMPLE,
        validators=sql_agent_validators(),
    ),
    "BASELINE": Treatment(
        description="Skill only, no CLAUDE.md (skill baseline)",
        skills=skill(GUIDANCE_POSITIVE),
        validators=sql_agent_validators(),
    ),

    # CLAUDE.md variations (single task only)
    "CLAUDE_MD_SKILLS": Treatment(
        description="CLAUDE.md says 'check skills' only",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS": Treatment(
        description="CLAUDE.md has pattern guidance (skill has guidance too)",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS_MOVED": Treatment(
        description="CLAUDE.md has pattern guidance (skill has NO guidance)",
        skills=skill(None),
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH": Treatment(
        description="CLAUDE.md: skills + patterns (skill has guidance too)",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_BOTH,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH_MOVED": Treatment(
        description="CLAUDE.md: skills + patterns (skill has NO guidance)",
        skills=skill(None),
        claude_md=CLAUDE_MD_BOTH,
        validators=sql_agent_validators(),
    ),

    # =========================================================================
    # CLASS 3: NOISE - Effects of Distractor Tasks
    # =========================================================================
    # Tests skill retention when distracted by unrelated tasks

    # Progressive noise (1, 2, 3 noise tasks)
    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns"],
        validators=noise_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components"],
        validators=noise_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components", "api-docs"],
        validators=noise_validators(),
    ),

}


# Noise treatments that should use search agent as second task
NOISE_TREATMENTS = {"NOISE_1", "NOISE_2", "NOISE_3"}


def build_sql_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build the prompt for a SQL treatment.

    - Non-NOISE treatments: Single SQL task only
    - NOISE treatments: SQL task + search agent (after noise tasks)

    Args:
        rep: Repetition number (unused here, but required by runner interface)
        run_id: Run ID (unused here, but required by runner interface)
    """
    if treatment_name and treatment_name in NOISE_TREATMENTS:
        return treatment.build_prompt(TASK1_PROMPT, TASK2_SEARCH_PROMPT)
    return treatment.build_prompt(TASK1_PROMPT)


def validate_sql_treatment(events: dict, test_dir: Path, treatment: Treatment):
    """Validate a SQL treatment."""
    return treatment.validate(events, test_dir)


# =============================================================================
# PRESETS - Grouped by Experiment Class
# =============================================================================

# CLASS 1: Reinforcement experiments
REINFORCEMENT_COMPARISON = ["GUIDANCE_POS", "GUIDANCE_NEG"]

# CLASS 2: CLAUDE.md experiments
CONTROL_COMPARISON = ["CONTROL", "BASELINE"]  # Does skill alone help?
CLAUDE_MD_COMPARISON = [                       # What CLAUDE.md content works?
    "BASELINE",
    "CLAUDE_MD_SKILLS",
    "CLAUDE_MD_PATTERNS", "CLAUDE_MD_PATTERNS_MOVED",
    "CLAUDE_MD_BOTH", "CLAUDE_MD_BOTH_MOVED",
]

# CLASS 3: Noise experiments
NOISE_COMPARISON = ["BASELINE", "NOISE_1", "NOISE_2", "NOISE_3"]

# All sections vs control
ALL_SECTIONS_VS_CONTROL = ["CONTROL", "ALL_SECTIONS"]

# All treatments
ALL_TREATMENTS = list(TREATMENTS.keys())
