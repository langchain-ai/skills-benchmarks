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
    GUIDANCE_POSITIVE,
    CLAUDE_MD_POSITIVE, CLAUDE_MD_NEGATIVE,
)

# =============================================================================
# SKILL SECTIONS
# =============================================================================

MINIMAL_SECTIONS = [
    FRONTMATTER, HEADER, QUICK_START, GUIDANCE_POSITIVE, LANGGRAPH_OVERVIEW,
]

BASIC_SECTIONS = FULL_LANGGRAPH_SECTIONS[:10]
FULL_SECTIONS = FULL_LANGGRAPH_SECTIONS


# =============================================================================
# PROMPTS
# =============================================================================

TASK1_PROMPT = """Build a multi-agent document analysis system using LangGraph.

Required Agents:
1. Router Agent: routes requests to specialists
2. Summarizer Agent: creates summaries
3. QA Agent: answers questions
4. Critic Agent: validates outputs

Requirements:
1. Supervisor pattern with Command-based handoffs
2. Maintain conversation state
3. Human-in-the-loop: pause for approval
4. Handle context overflow by summarizing old messages
5. Conditional routing based on intent
6. Print the compiled graph structure (using get_graph().draw_mermaid() or print_ascii())

Test: Analyze "Cloud Computing Architecture" - summary, follow-up question, critic validation.
Save to research_agent.py and run the test."""

TASK2_PROMPT = """Add a Fact-Checker Agent to verify claims against mock source data.
Print the updated graph structure showing the new agent.
Save to research_agent_2.py and demonstrate fact-checking."""


# =============================================================================
# VALIDATORS
# =============================================================================

# Core LangGraph patterns (ALL must be present)
LANGGRAPH_REQUIRED = {
    "StateGraph": "StateGraph",
    "TypedDict": "TypedDict",
    "@tool": "@tool decorator",
}

# Multi-agent patterns (at least one required for Agent 1)
MULTIAGENT_REQUIRED = {
    "Command": "uses Command for routing",
    "conditional_edges": "uses conditional routing",
    "add_node": "defines agent nodes",
}

# Graph compilation pattern
GRAPH_COMPILATION = {
    ".compile(": "compiles graph",
}

# Deprecated patterns (none allowed)
LANGGRAPH_FORBIDDEN = {
    "create_sql_agent": "uses deprecated create_sql_agent",
    "AgentExecutor": "uses deprecated AgentExecutor",
    "initialize_agent": "uses deprecated initialize_agent",
}


def langgraph_validators():
    """Standard validators for LangGraph treatments - runs files and checks output."""
    return [
        # Track skill invocation (don't fail, just note in stats)
        SkillInvokedValidator("langchain-agents", required=False),
        # Agent 1: Core LangGraph patterns (ALL required: StateGraph, TypedDict, @tool)
        PythonFileValidator(
            "research_agent.py", "Agent 1 Core",
            required=LANGGRAPH_REQUIRED,
            forbidden=LANGGRAPH_FORBIDDEN,
            require_all=True,
        ),
        # Agent 1: Multi-agent patterns + graph compilation
        PythonFileValidator(
            "research_agent.py", "Agent 1 Graph",
            required={**MULTIAGENT_REQUIRED, **GRAPH_COMPILATION},
        ),
        # Agent 1: LLM-based output quality check
        OutputQualityValidator(
            "research_agent.py", "Agent 1 Output",
            task_description="Multi-agent document analysis system with Router, Summarizer, QA, and Critic agents",
            expected_behavior="Should print graph structure (mermaid/ascii), show agent routing, produce summary about 'Cloud Computing Architecture', and show critic validation",
        ),
        # Agent 2: Core patterns + graph compilation
        PythonFileValidator(
            "research_agent_2.py", "Agent 2 Code",
            required={**LANGGRAPH_REQUIRED, **GRAPH_COMPILATION},
            forbidden=LANGGRAPH_FORBIDDEN,
            require_all=True,
        ),
        # Agent 2: LLM-based output quality check
        OutputQualityValidator(
            "research_agent_2.py", "Agent 2 Output",
            task_description="Extended multi-agent system with Fact-Checker agent",
            expected_behavior="Should print updated graph structure and demonstrate fact-checking against mock data",
        ),
        MetricsCollector(["research_agent.py", "research_agent_2.py"]),
    ]


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Control
    "CONTROL": Treatment(
        description="No skill (control)",
        validators=langgraph_validators(),
    ),
    "BASELINE": Treatment(
        description="Full LangGraph documentation",
        sections=FULL_SECTIONS,
        validators=langgraph_validators(),
    ),

    # Documentation levels
    "MINIMAL": Treatment(
        description="Minimal (just overview)",
        sections=MINIMAL_SECTIONS,
        validators=langgraph_validators(),
    ),
    "BASIC": Treatment(
        description="Basic (no detailed LangGraph)",
        sections=BASIC_SECTIONS,
        validators=langgraph_validators(),
    ),
    "FULL": Treatment(
        description="Full documentation",
        sections=FULL_SECTIONS,
        validators=langgraph_validators(),
    ),

    # CLAUDE.md
    "CLAUDE_MD_POS": Treatment(
        description="Full + CLAUDE.md positive",
        sections=FULL_SECTIONS,
        claude_md=CLAUDE_MD_POSITIVE,
        validators=langgraph_validators(),
    ),
    "CLAUDE_MD_NEG": Treatment(
        description="Full + CLAUDE.md negative",
        sections=FULL_SECTIONS,
        claude_md=CLAUDE_MD_NEGATIVE,
        validators=langgraph_validators(),
    ),

    # Noise (progressive: 1, 2, 3 noise tasks)
    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        sections=FULL_SECTIONS,
        noise_tasks=["docker-patterns"],
        validators=langgraph_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        sections=FULL_SECTIONS,
        noise_tasks=["docker-patterns", "react-components"],
        validators=langgraph_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        sections=FULL_SECTIONS,
        noise_tasks=["docker-patterns", "react-components", "api-docs"],
        validators=langgraph_validators(),
    ),

    # Stress tests
    "NOISE_CLAUDE_MD": Treatment(
        description="Full + noise + CLAUDE.md",
        sections=FULL_SECTIONS,
        claude_md=CLAUDE_MD_POSITIVE,
        noise_tasks=["docker-patterns"],
        validators=langgraph_validators(),
    ),
    "MINIMAL_NOISE": Treatment(
        description="Minimal + noise",
        sections=MINIMAL_SECTIONS,
        noise_tasks=["docker-patterns"],
        validators=langgraph_validators(),
    ),
}


def build_langgraph_prompt(treatment: Treatment) -> str:
    """Build the prompt for a LangGraph treatment."""
    return treatment.build_prompt(TASK1_PROMPT, TASK2_PROMPT)


def validate_langgraph_treatment(events: dict, test_dir: Path, treatment: Treatment):
    """Validate a LangGraph treatment."""
    return treatment.validate(events, test_dir)


# Presets
CONTROL_COMPARISON = ["CONTROL", "BASELINE"]
DOC_LEVEL_COMPARISON = ["MINIMAL", "BASIC", "FULL"]
CLAUDE_MD_COMPARISON = ["BASELINE", "CLAUDE_MD_POS", "CLAUDE_MD_NEG"]
NOISE_COMPARISON = ["BASELINE", "NOISE_1", "NOISE_2", "NOISE_3"]
STRESS_COMPARISON = ["MINIMAL", "MINIMAL_NOISE", "NOISE_CLAUDE_MD"]
ALL_TREATMENTS = list(TREATMENTS.keys())
