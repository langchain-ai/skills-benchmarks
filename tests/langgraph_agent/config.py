"""LangGraph Agent experiment.

Tests whether Claude can generate complex multi-agent LangGraph code
with proper patterns (StateGraph, Command, conditional routing).
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
    FRONTMATTER, HEADER, QUICK_START, LANGGRAPH_OVERVIEW,
    FULL_LANGGRAPH_SECTIONS,
    GUIDANCE_POSITIVE, GUIDANCE_NEGATIVE,
    CLAUDE_MD_SKILLS_ONLY, CLAUDE_MD_BOTH,
)

# =============================================================================
# SKILL SECTIONS
# =============================================================================

BASE_SECTIONS = FULL_LANGGRAPH_SECTIONS


def sections_guidance(guidance):
    """Build sections list with guidance inserted after QUICK_START."""
    # Insert guidance after the third element (QUICK_START)
    result = BASE_SECTIONS.copy()
    if guidance:
        result.insert(3, guidance)
    return result


def skill(guidance):
    """Build skills dict with langchain-agents skill."""
    return {"langchain-agents": sections_guidance(guidance)}


# =============================================================================
# PROMPTS
# =============================================================================

TASK1_PROMPT = """Build a multi-agent research system using LangGraph.

Required Agents:
1. Supervisor: Routes requests and decides when task is complete
2. Researcher: Uses TavilySearchResults tool to gather information
3. Writer: Synthesizes research into coherent summaries

Requirements:
1. Use LangGraph's graph-based approach for agent orchestration
2. Implement a supervisor pattern where one agent coordinates others
3. Use TavilySearchResults from langchain_community.tools.tavily_search
4. Print the graph structure with get_graph() to verify all nodes are defined
5. Run a test query and show the output

Test with: "Research 'Cloud Computing' and write a summary with 3 key benefits."

Save to research_agent.py and run the test.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""

TASK2_PROMPT = """Add a Critic agent that reviews the Writer's output.

Requirements:
1. New Critic node that validates/reviews the written summary
2. Supervisor can now route to Researcher, Writer, or Critic
3. Print the graph structure to verify the new node exists

Save to research_agent_2.py and demonstrate the critic reviewing the summary.

IMPORTANT: Run files directly (not in background). If code fails after 2 attempts to fix, save the file and report the error - do not enter debug loops."""


# =============================================================================
# VALIDATORS
# =============================================================================

# Core LangGraph patterns (ALL must be present)
LANGGRAPH_REQUIRED = {
    "StateGraph": "uses StateGraph",
    "TypedDict": "uses TypedDict",
}

# Multi-agent patterns
MULTIAGENT_PATTERNS = {
    "add_node": "defines nodes",
}

# Graph compilation
GRAPH_EXECUTION = {
    ".compile(": "compiles graph",
    "get_graph()": "inspects graph structure",
}

# Deprecated patterns (none allowed)
LANGGRAPH_FORBIDDEN = {
    "create_sql_agent": "uses deprecated create_sql_agent",
    "AgentExecutor": "uses deprecated AgentExecutor",
    "initialize_agent": "uses deprecated initialize_agent",
}


def langgraph_validators():
    """Validators for LangGraph multi-agent treatments."""
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        # Agent 1: Core patterns
        PythonFileValidator(
            "research_agent.py", "Agent 1 Core",
            required=LANGGRAPH_REQUIRED,
            forbidden=LANGGRAPH_FORBIDDEN,
            require_all=True,
        ),
        # Agent 1: Graph structure code
        PythonFileValidator(
            "research_agent.py", "Agent 1 Graph",
            required={**MULTIAGENT_PATTERNS, **GRAPH_EXECUTION},
        ),
        # Agent 1: Output validation
        OutputQualityValidator(
            "research_agent.py", "Agent 1 Output",
            task_description="Multi-agent system with Supervisor, Researcher, and Writer nodes",
            expected_behavior="Output should print a list of node names (from get_graph().nodes.keys()) showing at least 3 custom nodes, and produce a summary about Cloud Computing",
        ),
        # Agent 2: Core patterns
        PythonFileValidator(
            "research_agent_2.py", "Agent 2 Core",
            required={**LANGGRAPH_REQUIRED, **GRAPH_EXECUTION},
            forbidden=LANGGRAPH_FORBIDDEN,
            require_all=True,
        ),
        # Agent 2: Output validation
        OutputQualityValidator(
            "research_agent_2.py", "Agent 2 Output",
            task_description="Extended multi-agent system with Critic node added",
            expected_behavior="Output should print a list of node names showing at least 4 custom nodes, and demonstrate the critic reviewing the summary",
        ),
        MetricsCollector(["research_agent.py", "research_agent_2.py"]),
    ]


# =============================================================================
# TREATMENTS
# =============================================================================
# Organized into 3 experiment classes:
#   1. REINFORCEMENT: Effects of positive vs negative guidance
#   2. CLAUDE_MD: Effects of CLAUDE.md presence and content
#   3. NOISE: Effects of distractor tasks
# =============================================================================

TREATMENTS = {
    # =========================================================================
    # CLASS 1: REINFORCEMENT - Positive vs Negative Guidance
    # =========================================================================

    "GUIDANCE_POS": Treatment(
        description="Skill with positive guidance",
        skills=skill(GUIDANCE_POSITIVE),
        validators=langgraph_validators(),
    ),
    "GUIDANCE_NEG": Treatment(
        description="Skill with negative guidance",
        skills=skill(GUIDANCE_NEGATIVE),
        validators=langgraph_validators(),
    ),

    # =========================================================================
    # CLASS 2: CLAUDE_MD - Effects of CLAUDE.md
    # =========================================================================

    "CONTROL": Treatment(
        description="No skill, no CLAUDE.md",
        validators=langgraph_validators(),
    ),
    "BASELINE": Treatment(
        description="Skill only, no CLAUDE.md",
        skills=skill(GUIDANCE_POSITIVE),
        validators=langgraph_validators(),
    ),
    "CLAUDE_MD_SKILLS": Treatment(
        description="CLAUDE.md: check skills only",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=langgraph_validators(),
    ),
    "CLAUDE_MD_BOTH": Treatment(
        description="CLAUDE.md: skills + patterns",
        skills=skill(GUIDANCE_POSITIVE),
        claude_md=CLAUDE_MD_BOTH,
        validators=langgraph_validators(),
    ),

    # =========================================================================
    # CLASS 3: NOISE - Effects of Distractor Tasks
    # =========================================================================

    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns"],
        validators=langgraph_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components"],
        validators=langgraph_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        skills=skill(GUIDANCE_POSITIVE),
        noise_tasks=["docker-patterns", "react-components", "api-docs"],
        validators=langgraph_validators(),
    ),
}


def build_langgraph_prompt(treatment: Treatment) -> str:
    """Build the prompt for a LangGraph treatment."""
    return treatment.build_prompt(TASK1_PROMPT, TASK2_PROMPT)


# =============================================================================
# PRESETS
# =============================================================================

REINFORCEMENT_COMPARISON = ["GUIDANCE_POS", "GUIDANCE_NEG"]
CONTROL_COMPARISON = ["CONTROL", "BASELINE"]
CLAUDE_MD_COMPARISON = ["BASELINE", "CLAUDE_MD_SKILLS", "CLAUDE_MD_BOTH"]
NOISE_COMPARISON = ["BASELINE", "NOISE_1", "NOISE_2", "NOISE_3"]
ALL_TREATMENTS = list(TREATMENTS.keys())
