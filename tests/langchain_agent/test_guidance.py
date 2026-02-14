"""Guidance treatments (positive vs negative framing in skills).

Tests whether framing matters: "DO use modern patterns" vs "DON'T use deprecated".
"""

from scaffold import Treatment
from skill_constructs.parser import skill_config

from tests.langchain_agent.config import (
    agents_skill,
    sections_with_guidance,
    GUIDANCE_POSITIVE,
    GUIDANCE_NEGATIVE,
    CLAUDE_MD_SKILLS_REQUIRED,
    sql_agent_validators,
    TASK1_PROMPT,
)


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    "GUIDANCE_POS": Treatment(
        description="Skill with positive guidance (DO use modern patterns)",
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_POSITIVE)},
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),
    "GUIDANCE_NEG": Treatment(
        description="Skill with negative guidance (DON'T use deprecated)",
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_NEGATIVE)},
        claude_md=CLAUDE_MD_SKILLS_REQUIRED,
        validators=sql_agent_validators(),
    ),
}


# =============================================================================
# PRESETS
# =============================================================================

GUIDANCE_COMPARISON = list(TREATMENTS.keys())


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build prompt for guidance treatments."""
    return treatment.build_prompt(TASK1_PROMPT)


# =============================================================================
# VALIDATOR (module-level for pickling)
# =============================================================================

def validate_treatment(events: dict, test_dir, treatment_name: str, outputs: dict):
    """Validate using the treatment's validators."""
    treatment = TREATMENTS.get(treatment_name)
    if treatment:
        return treatment.validate(events, test_dir, outputs)
    return [], [f"Unknown treatment: {treatment_name}"]


# =============================================================================
# CLI RUNNER
# =============================================================================

if __name__ == "__main__":
    from tests.langchain_agent.runner import run_experiment
    import argparse

    parser = argparse.ArgumentParser(description="Guidance experiment (positive vs negative)")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-t", "--treatments", nargs="+", help="Treatment names")
    parser.add_argument("-r", "--repeat", type=int, default=1, help="Repetitions")
    parser.add_argument("-w", "--workers", type=int, default=3, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per run")
    args = parser.parse_args()

    run_experiment(
        treatments=TREATMENTS,
        build_prompt_func=build_prompt,
        validate_func=validate_treatment,
        experiment_name="guidance_experiment",
        treatment_names=args.treatments,
        repeat=args.repeat,
        workers=args.workers,
        timeout=args.timeout,
        model=args.model,
    )
