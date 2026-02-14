"""Advanced LangSmith Synergy treatments (3 skills: trace + dataset + evaluator).

Each treatment defines its own section selections inline.
"""

from scaffold import Treatment
from skill_constructs.parser import skill_config
from skill_constructs import CLAUDE_SAMPLE

from tests.langsmith_synergy.config import (
    skills,
    without_related_skills,
    advanced_validators,
    CLAUDE_MD_SKILLS_ONLY,
    CLAUDE_MD_WORKFLOW_ADVANCED,
    ADVANCED_PROMPT_TEMPLATE,
)

# =============================================================================
# SECTION SELECTIONS FOR ADVANCED TREATMENTS
# =============================================================================

# Trace: all sections (primary skill)
trace_all = skills["trace"]["all"]
trace_no_hints = without_related_skills(trace_all)

# Dataset: curated subset (exclude detailed examples)
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

# Evaluator: curated subset (exclude detailed examples)
evaluator_curated = [
    skills["evaluator"]["sections"]["frontmatter"],
    skills["evaluator"]["sections"]["oneliner"],
    skills["evaluator"]["sections"]["setup"],
    skills["evaluator"]["sections"]["evaluator_format"],
    skills["evaluator"]["sections"]["evaluator_types"],
    skills["evaluator"]["sections"]["best_practices"],
    skills["evaluator"]["sections"]["related_skills"],
]
evaluator_no_hints = without_related_skills(evaluator_curated)


# =============================================================================
# TREATMENTS
# =============================================================================

TREATMENTS = {
    # Control: No skills, no CLAUDE.md (pure baseline - Claude's native ability)
    "ADV_CONTROL": Treatment(
        description="No skills, no CLAUDE.md (pure baseline)",
        skills={},
        validators=advanced_validators(),
    ),

    # Baseline: Skills WITHOUT workflow hints, no CLAUDE.md (hardest - no cross-references)
    "ADV_BASELINE": Treatment(
        description="Skills without workflow hints, no CLAUDE.md (no cross-references)",
        skills={
            "langsmith-trace": skill_config(trace_no_hints, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_no_hints, skills["dataset"]["scripts_dir"]),
            "langsmith-evaluator": skill_config(evaluator_no_hints, skills["evaluator"]["scripts_dir"]),
        },
        validators=advanced_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "ADV_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": skill_config(trace_no_hints, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_no_hints, skills["dataset"]["scripts_dir"]),
            "langsmith-evaluator": skill_config(evaluator_no_hints, skills["evaluator"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_WORKFLOW_ADVANCED,
        validators=advanced_validators(),
    ),

    # Skills only: Workflow hints in skills (related_skills section), minimal CLAUDE.md
    "ADV_SKILLS": Treatment(
        description="Workflow hints in skills, minimal CLAUDE.md",
        skills={
            "langsmith-trace": skill_config(trace_all, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
            "langsmith-evaluator": skill_config(evaluator_curated, skills["evaluator"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=advanced_validators(),
    ),

    # Both: Workflow rules in CLAUDE.md AND skill hints (reinforcement)
    "ADV_BOTH": Treatment(
        description="Workflow rules in CLAUDE.md AND skill hints",
        skills={
            "langsmith-trace": skill_config(trace_all, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
            "langsmith-evaluator": skill_config(evaluator_curated, skills["evaluator"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_WORKFLOW_ADVANCED,
        validators=advanced_validators(),
    ),

    # All sections: Complete skill content + full CLAUDE.md sample
    "ADV_ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={
            "langsmith-trace": skill_config(skills["trace"]["all"], skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(skills["dataset"]["all"], skills["dataset"]["scripts_dir"]),
            "langsmith-evaluator": skill_config(skills["evaluator"]["all"], skills["evaluator"]["scripts_dir"]),
        },
        claude_md=CLAUDE_SAMPLE,
        validators=advanced_validators(),
    ),
}


# =============================================================================
# PRESETS (for runner)
# =============================================================================

ADVANCED_COMPARISON = list(TREATMENTS.keys())
ADV_ALL_SECTIONS_VS_CONTROL = ["ADV_CONTROL", "ADV_ALL_SECTIONS"]


# =============================================================================
# PROMPT BUILDER
# =============================================================================

def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1, run_id: str = None) -> str:
    """Build prompt for advanced treatments."""
    dataset_name = f"test-{run_id}" if run_id else "test-dataset"
    prompt = ADVANCED_PROMPT_TEMPLATE.format(run_id=dataset_name)
    return treatment.build_prompt(prompt)


# =============================================================================
# CLI RUNNER
# =============================================================================

if __name__ == "__main__":
    from tests.langsmith_synergy.runner import main_cli
    main_cli(TREATMENTS, build_prompt, "advanced_synergy")
