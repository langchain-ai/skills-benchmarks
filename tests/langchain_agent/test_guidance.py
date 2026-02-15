"""Guidance treatments (positive vs negative framing in skills).

Tests whether framing matters: "DO use modern patterns" vs "DON'T use deprecated".

Run with: pytest tests/langchain_agent/test_guidance.py -v
Parallel:  pytest tests/langchain_agent/test_guidance.py -n 3
"""

import pytest

from scaffold import Treatment
from scaffold.python import extract_events, parse_output

from tests.langchain_agent.config import (
    with_quickstart,
    QUICK_START_POSITIVE,
    QUICK_START_NEGATIVE,
    CLAUDE_MD_SKILLS_REQUIRED,
    sql_agent_validators,
    TASK1_PROMPT,
    ENVIRONMENT_DIR,
)


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
