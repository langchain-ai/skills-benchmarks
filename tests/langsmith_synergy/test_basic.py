"""Basic LangSmith Synergy treatments (2 skills: trace + dataset).

Each treatment defines its own section selections inline.
"""

from scaffold import Treatment
from skill_constructs.parser import skill_config
from skill_constructs import CLAUDE_SAMPLE

from tests.langsmith_synergy.config import (
    skills,
    without_related_skills,
    basic_validators,
    CLAUDE_MD_SKILLS_ONLY,
    CLAUDE_MD_WORKFLOW_BASIC,
    BASIC_PROMPT_TEMPLATE,
)

# =============================================================================
# SECTION SELECTIONS FOR BASIC TREATMENTS
# =============================================================================

# Trace: all sections (primary skill for this experiment)
trace_all = skills["trace"]["all"]
trace_no_hints = without_related_skills(trace_all)

# Dataset: curated subset (exclude detailed examples to stress test Claude)
dataset_curated = [
    skills["dataset"]["sections"]["frontmatter"],
    skills["dataset"]["sections"]["oneliner"],
    skills["dataset"]["sections"]["setup"],
    skills["dataset"]["sections"]["input_format"],
    skills["dataset"]["sections"]["usage"],
    skills["dataset"]["sections"]["extraction_priority"],
    skills["dataset"]["sections"]["trace_hierarchy"],
    skills["dataset"]["sections"]["dataset_types_overview"],
    skills["dataset"]["sections"]["related_skills"],
]
dataset_no_hints = without_related_skills(dataset_curated)


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Control: No skills, no CLAUDE.md (pure baseline - Claude's native ability)
    "BASIC_CONTROL": Treatment(
        description="No skills, no CLAUDE.md (pure baseline)",
        skills={},
        validators=basic_validators(),
    ),

    # Baseline: Skills WITHOUT workflow hints, no CLAUDE.md (hardest - no cross-references)
    "BASIC_BASELINE": Treatment(
        description="Skills without workflow hints, no CLAUDE.md (no cross-references)",
        skills={
            "langsmith-trace": skill_config(trace_no_hints, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_no_hints, skills["dataset"]["scripts_dir"]),
        },
        validators=basic_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "BASIC_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": skill_config(trace_no_hints, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_no_hints, skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_WORKFLOW_BASIC,
        validators=basic_validators(),
    ),

    # Skills only: Workflow hints in skills (related_skills section), minimal CLAUDE.md
    "BASIC_SKILLS": Treatment(
        description="Workflow hints in skills, minimal CLAUDE.md",
        skills={
            "langsmith-trace": skill_config(trace_all, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=basic_validators(),
    ),

    # Both: Workflow rules in CLAUDE.md AND skill hints (reinforcement)
    "BASIC_BOTH": Treatment(
        description="Workflow rules in CLAUDE.md AND skill hints",
        skills={
            "langsmith-trace": skill_config(trace_all, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_WORKFLOW_BASIC,
        validators=basic_validators(),
    ),

    # All sections: Complete skill content + full CLAUDE.md sample
    "BASIC_ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={
            "langsmith-trace": skill_config(skills["trace"]["all"], skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(skills["dataset"]["all"], skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_SAMPLE,
        validators=basic_validators(),
    ),
}


# =============================================================================
# PRESETS (for runner)
# =============================================================================

BASIC_COMPARISON = list(TREATMENTS.keys())
BASIC_ALL_SECTIONS_VS_CONTROL = ["BASIC_CONTROL", "BASIC_ALL_SECTIONS"]


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build prompt for basic treatments."""
    dataset_name = f"test-{run_id}" if run_id else "test-dataset"
    prompt = BASIC_PROMPT_TEMPLATE.format(run_id=dataset_name)
    return treatment.build_prompt(prompt)


# =============================================================================
# VALIDATOR (module-level for pickling in multiprocessing)
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
    import time
    from scaffold import run_experiment
    from tests.langsmith_synergy.config import ENVIRONMENT_DIR, REQUIRED_FILES, BASIC_COLUMNS
    from tests.langsmith_synergy.fixtures.hooks import (
        generate_traces, generate_ground_truth, cleanup_langsmith_datasets,
    )

    parser = argparse.ArgumentParser(description="Basic synergy experiment")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-t", "--treatments", nargs="+", help="Treatment names")
    parser.add_argument("-r", "--repeat", type=int, default=1, help="Repetitions")
    parser.add_argument("-w", "--workers", type=int, default=3, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per run")
    parser.add_argument("--skip-traces", action="store_true", help="Skip trace generation")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip cleanup")
    args = parser.parse_args()

    def pre_run():
        if not args.skip_traces:
            if not generate_traces():
                print("WARNING: Trace generation had errors. Continuing anyway...")
            print("Waiting 10s for LangSmith to index traces...")
            time.sleep(10)

    run_experiment(
        treatments=TREATMENTS,
        build_prompt_func=build_prompt,
        validate_func=validate_treatment,
        experiment_name="basic_synergy",
        environment_dir=ENVIRONMENT_DIR,
        required_files=REQUIRED_FILES,
        columns=BASIC_COLUMNS,
        treatment_names=args.treatments,
        repeat=args.repeat,
        workers=args.workers,
        timeout=args.timeout,
        model=args.model,
        pre_run=pre_run,
        post_run=None if args.skip_cleanup else cleanup_langsmith_datasets,
        ground_truth_func=generate_ground_truth,
    )
