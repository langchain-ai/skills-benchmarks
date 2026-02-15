"""Example Python benchmark test using pytest.

Demonstrates the test pattern for skill benchmarks:
1. Load skills from skill.md files using parser
2. Define treatments (skill configurations to test)
3. Set up test context with skills/CLAUDE.md
4. Run Claude with prompt
5. Parse output and extract events
6. Validate results

Run with: uv run pytest tests/example/test_guidance.py -v
Parallel:  uv run pytest tests/example/test_guidance.py -v -n 3
"""

from pathlib import Path

import pytest

from scaffold import (
    MetricsCollector,
    PythonFileValidator,
    SkillInvokedValidator,
    Treatment,
)
from scaffold.python import extract_events, parse_output
from skills.parser import load_skill

# =============================================================================
# LOAD SKILLS
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"

# Load skill from skill.md file - provides ["all"] (all sections) and ["sections"] (by tag)
langchain_skill = load_skill(SKILL_BASE / "langchain_basic")

# =============================================================================
# PROMPT & VALIDATORS
# =============================================================================

TASK_PROMPT = """Create a simple LangChain agent that:
1. Uses the @tool decorator to define a calculator tool
2. Uses create_agent to build the agent
3. Invokes the agent with a test question

Save to agent.py and run it."""

REQUIRED_PATTERNS = {
    "@tool": "uses @tool decorator",
    "create_agent": "uses create_agent",
}


def create_validators():
    return [
        SkillInvokedValidator("langchain-agents", required=False),
        PythonFileValidator(
            "agent.py",
            "LangChain Agent",
            required=REQUIRED_PATTERNS,
            require_all=True,
        ),
        MetricsCollector(["agent.py"]),
    ]


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Control: No skill provided. Tests baseline model behavior.
    "CONTROL": Treatment(
        description="No skill (pure control)",
        validators=create_validators(),
    ),
    # All sections: Full skill content.
    "ALL_SECTIONS": Treatment(
        description="With langchain-agents skill (all sections)",
        skills={
            # Use all sections from the skill
            "langchain-agents": langchain_skill["all"],
        },
        validators=create_validators(),
    ),
    # Minimal: Only specific sections. Tests minimal guidance.
    "MINIMAL": Treatment(
        description="With langchain-agents skill (minimal sections)",
        skills={
            # Select specific sections by tag name
            "langchain-agents": [
                langchain_skill["sections"]["frontmatter"],
                langchain_skill["sections"]["oneliner"],
                langchain_skill["sections"]["quick_start"],
            ],
        },
        validators=create_validators(),
    ),
}

# =============================================================================
# ENVIRONMENT
# =============================================================================

ENVIRONMENT_DIR = Path(__file__).parent.parent / "bench_lc_basic" / "environment"


@pytest.fixture
def environment_dir():
    """Path to environment directory with Dockerfile, requirements.txt, etc."""
    return ENVIRONMENT_DIR


# =============================================================================
# TEST
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

    # 1. Set up test context
    setup_test_context(
        skills=treatment.skills,
        claude_md=treatment.claude_md,
        environment_dir=environment_dir,
    )

    # 2. Run Claude
    result = run_claude(TASK_PROMPT, timeout=300)

    # 3. Parse output and extract events
    events = extract_events(parse_output(result.stdout))

    # 4. Validate
    passed, failed = treatment.validate(events, test_dir, {})

    # 5. Record results
    record_result(events, passed, failed)

    # 6. Assert
    assert not failed, f"Validation failed: {failed}"
