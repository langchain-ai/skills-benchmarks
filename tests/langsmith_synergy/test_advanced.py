"""Advanced LangSmith Synergy treatments (3 skills: trace + dataset + evaluator).

Each treatment defines its own section selections inline.

Run with: pytest tests/langsmith_synergy/test_advanced.py -v
Parallel:  pytest tests/langsmith_synergy/test_advanced.py -n 3
"""

import uuid
import pytest

from scaffold import Treatment
from scaffold.python import extract_events, parse_output
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
# TESTS
# =============================================================================

@pytest.mark.parametrize("treatment_name", list(TREATMENTS.keys()))
def test_treatment(
    treatment_name,
    verify_environment,
    langsmith_traces,
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

    # Build prompt with unique run_id for dataset naming
    run_id = str(uuid.uuid4())[:8]
    dataset_name = f"test-{run_id}"
    prompt = ADVANCED_PROMPT_TEMPLATE.format(run_id=dataset_name)
    prompt = treatment.build_prompt(prompt)

    # Run Claude (automatically saves raw output)
    result = run_claude(prompt, timeout=600)

    # Parse output
    events = extract_events(parse_output(result.stdout))

    # Validate (pass trace_id_map for remapping expected -> actual trace IDs)
    trace_id_map = langsmith_traces.get("trace_id_map", {})
    outputs = {"run_id": run_id, "trace_id_map": trace_id_map}
    passed, failed = treatment.validate(events, test_dir, outputs)

    # Record results (saves events, artifacts, reports)
    record_result(events, passed, failed, run_id=run_id)

    # Assert
    assert not failed, f"Validation failed: {failed}"
