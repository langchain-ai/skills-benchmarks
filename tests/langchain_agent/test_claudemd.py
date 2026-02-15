"""CLAUDE.md treatments (effects of CLAUDE.md presence and content).

Tests whether CLAUDE.md is needed and what instructions work best.

Run with: pytest tests/langchain_agent/test_claudemd.py -v
Parallel:  pytest tests/langchain_agent/test_claudemd.py -n 3
"""

import pytest

from scaffold import Treatment
from scaffold.python import extract_events, parse_output
from skill_constructs import CLAUDE_SAMPLE

from tests.langchain_agent.config import (
    with_quickstart,
    QUICK_START_POSITIVE,
    FULL_SECTIONS,
    CLAUDE_MD_SKILLS_ONLY,
    CLAUDE_MD_PATTERNS_POSITIVE,
    CLAUDE_MD_BOTH,
    sql_agent_validators,
    TASK1_PROMPT,
    ENVIRONMENT_DIR,
)


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Baselines
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
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        validators=sql_agent_validators(),
    ),

    # CLAUDE.md variations
    "CLAUDE_MD_SKILLS": Treatment(
        description="CLAUDE.md says 'check skills' only",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS": Treatment(
        description="CLAUDE.md has pattern guidance (skill has guidance too)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS_MOVED": Treatment(
        description="CLAUDE.md has pattern guidance (skill has NO guidance)",
        skills={"langchain-agents": with_quickstart(None)},
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH": Treatment(
        description="CLAUDE.md: skills + patterns (skill has guidance too)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        claude_md=CLAUDE_MD_BOTH,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH_MOVED": Treatment(
        description="CLAUDE.md: skills + patterns (skill has NO guidance)",
        skills={"langchain-agents": with_quickstart(None)},
        claude_md=CLAUDE_MD_BOTH,
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
