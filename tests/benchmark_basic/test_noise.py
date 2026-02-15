"""Noise treatments (effects of distractor tasks on skill retention).

Tests skill retention when distracted by unrelated tasks.

Run with: pytest tests/langchain_agent/test_noise.py -v
Parallel:  pytest tests/langchain_agent/test_noise.py -n 3
"""

import pytest

from scaffold import Treatment
from scaffold.python import extract_events, parse_output
from tests.benchmark_basic.config import (
    ENVIRONMENT_DIR,
    QUICK_START_POSITIVE,
    TASK1_PROMPT,
    TASK2_SEARCH_PROMPT,
    noise_validators,
    with_quickstart,
)
from tests.noise import get_tasks

# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    "NOISE_BASELINE": Treatment(
        description="Baseline for noise comparison (no noise)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        validators=noise_validators(),
    ),
    "NOISE_1": Treatment(
        description="1 noise task (Docker)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        noise_tasks=get_tasks(["docker-patterns"]),
        validators=noise_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        noise_tasks=get_tasks(["docker-patterns", "react-components"]),
        validators=noise_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        noise_tasks=get_tasks(["docker-patterns", "react-components", "api-docs"]),
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
