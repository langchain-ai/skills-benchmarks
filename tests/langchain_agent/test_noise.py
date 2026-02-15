"""Noise treatments (effects of distractor tasks on skill retention).

Tests skill retention when distracted by unrelated tasks.
"""

from scaffold import Treatment

from tests.langchain_agent.config import (
    with_quickstart,
    QUICK_START_POSITIVE,
    noise_validators,
    TASK1_PROMPT,
    TASK2_SEARCH_PROMPT,
)


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
        noise_tasks=["docker-patterns"],
        validators=noise_validators(),
    ),
    "NOISE_2": Treatment(
        description="2 noise tasks (Docker + React)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        noise_tasks=["docker-patterns", "react-components"],
        validators=noise_validators(),
    ),
    "NOISE_3": Treatment(
        description="3 noise tasks (Docker + React + API)",
        skills={"langchain-agents": with_quickstart(QUICK_START_POSITIVE)},
        noise_tasks=["docker-patterns", "react-components", "api-docs"],
        validators=noise_validators(),
    ),
}


# =============================================================================
# PRESETS
# =============================================================================

NOISE_COMPARISON = list(TREATMENTS.keys())


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build prompt for noise treatments (SQL + search agent tasks)."""
    return treatment.build_prompt(TASK1_PROMPT, TASK2_SEARCH_PROMPT)


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
    import argparse
    from scaffold import run_experiment
    from tests.langchain_agent.config import ENVIRONMENT_DIR, REQUIRED_FILES, COLUMNS

    parser = argparse.ArgumentParser(description="Noise experiment (distractor tasks)")
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
        experiment_name="noise_experiment",
        environment_dir=ENVIRONMENT_DIR,
        required_files=REQUIRED_FILES,
        columns=COLUMNS,
        treatment_names=args.treatments,
        repeat=args.repeat,
        workers=args.workers,
        timeout=args.timeout,
        model=args.model,
    )
