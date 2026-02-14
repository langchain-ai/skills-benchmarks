"""CLAUDE.md treatments (effects of CLAUDE.md presence and content).

Tests whether CLAUDE.md is needed and what instructions work best.
"""

from scaffold import Treatment
from skill_constructs import CLAUDE_SAMPLE

from tests.langchain_agent.config import (
    agents_skill,
    sections_with_guidance,
    GUIDANCE_POSITIVE,
    FULL_SECTIONS,
    CLAUDE_MD_SKILLS_ONLY,
    CLAUDE_MD_PATTERNS_POSITIVE,
    CLAUDE_MD_BOTH,
    sql_agent_validators,
    TASK1_PROMPT,
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
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_POSITIVE)},
        validators=sql_agent_validators(),
    ),

    # CLAUDE.md variations
    "CLAUDE_MD_SKILLS": Treatment(
        description="CLAUDE.md says 'check skills' only",
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_POSITIVE)},
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS": Treatment(
        description="CLAUDE.md has pattern guidance (skill has guidance too)",
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_POSITIVE)},
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_PATTERNS_MOVED": Treatment(
        description="CLAUDE.md has pattern guidance (skill has NO guidance)",
        skills={"langchain-agents": sections_with_guidance(None)},
        claude_md=CLAUDE_MD_PATTERNS_POSITIVE,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH": Treatment(
        description="CLAUDE.md: skills + patterns (skill has guidance too)",
        skills={"langchain-agents": sections_with_guidance(GUIDANCE_POSITIVE)},
        claude_md=CLAUDE_MD_BOTH,
        validators=sql_agent_validators(),
    ),
    "CLAUDE_MD_BOTH_MOVED": Treatment(
        description="CLAUDE.md: skills + patterns (skill has NO guidance)",
        skills={"langchain-agents": sections_with_guidance(None)},
        claude_md=CLAUDE_MD_BOTH,
        validators=sql_agent_validators(),
    ),
}


# =============================================================================
# PRESETS
# =============================================================================

CLAUDEMD_COMPARISON = list(TREATMENTS.keys())
CONTROL_COMPARISON = ["CONTROL", "BASELINE"]
ALL_SECTIONS_VS_CONTROL = ["CONTROL", "ALL_SECTIONS"]


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build prompt for CLAUDE.md treatments."""
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

    parser = argparse.ArgumentParser(description="CLAUDE.md experiment")
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
        experiment_name="claudemd_experiment",
        treatment_names=args.treatments,
        repeat=args.repeat,
        workers=args.workers,
        timeout=args.timeout,
        model=args.model,
    )
