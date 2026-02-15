"""Basic LangSmith Synergy treatments (2 skills: trace + dataset).

Each treatment defines its own section selections inline.

Run with: pytest tests/bench_ls_multiskill/test_basic.py -v
Parallel:  pytest tests/bench_ls_multiskill/test_basic.py -n 3
"""

import uuid
from pathlib import Path

import pytest

from scaffold import MetricsCollector, SkillInvokedValidator, Treatment
from scaffold.python import extract_events, parse_output
from skills import CLAUDE_FULL
from skills.parser import load_skill, skill_config
from tests.bench_ls_multiskill.validation.validators import (
    DatasetStructureValidator,
    SkillScriptValidator,
    TrajectoryAccuracyValidator,
)

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"


def _load_skills():
    """Load all skills from skill.md files."""
    return {
        "trace": load_skill(SKILL_BASE / "langsmith_trace"),
        "dataset": load_skill(SKILL_BASE / "langsmith_dataset"),
    }


skills = _load_skills()


# =============================================================================
# SECTION HELPERS
# =============================================================================


def without_related_skills(sections):
    """Filter out related_skills sections (cross-skill references)."""

    def is_related(s):
        return s and (
            "**langsmith-trace**:" in s
            or "**langsmith-dataset**:" in s
            or "**langsmith-evaluator**:" in s
        )

    return [s for s in sections if not is_related(s)]


# =============================================================================
# CONSTANTS
# =============================================================================

WORKFLOW_RULE_BASIC = """## LangSmith Skills

This project has LangSmith skills for working with traces and datasets:

- **langsmith-trace**: Query and analyze traces from LangSmith projects
- **langsmith-dataset**: Generate datasets from trace data

Note: The dataset skill requires trace data to work with. Use the trace skill first to understand available data before generating datasets."""

CLAUDE_MD_SKILLS_ONLY = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
"""

CLAUDE_MD_WORKFLOW_BASIC = CLAUDE_MD_SKILLS_ONLY + "\n" + WORKFLOW_RULE_BASIC

BASIC_PROMPT_TEMPLATE = """Create a trajectory dataset with 5 examples from the 5 most recent traces in our LangSmith project.

Output: trajectory_dataset.json (upload as "{run_id}" to LangSmith)

Run any code you write directly."""


# =============================================================================
# VALIDATORS
# =============================================================================


def basic_validators():
    """Validators for basic test (trace + dataset)."""
    return [
        SkillInvokedValidator("langsmith-trace", required=False),
        SkillInvokedValidator("langsmith-dataset", required=False),
        SkillScriptValidator(
            {
                "query_traces.py": "query_traces.py",
                "generate_datasets.py": "generate_datasets.py",
            }
        ),
        DatasetStructureValidator(
            filename="trajectory_dataset.json",
            min_examples=1,
            dataset_type="trajectory",
        ),
        TrajectoryAccuracyValidator(
            filename="trajectory_dataset.json",
            expected_filename="expected_dataset.json",
            verify_upload=True,
            upload_prefix="test-",
        ),
        MetricsCollector(),
    ]


# =============================================================================
# SECTION SELECTIONS FOR BASIC TREATMENTS
# =============================================================================

# Trace: curated subset (matches old DEFAULT_SECTIONS - excludes detailed examples)
trace_curated = [
    skills["trace"]["sections"]["frontmatter"],
    skills["trace"]["sections"]["oneliner"],
    skills["trace"]["sections"]["setup"],
    skills["trace"]["sections"]["trace_langchain_oss"],
    skills["trace"]["sections"]["traces_vs_runs"],
    skills["trace"]["sections"]["command_structure"],
    skills["trace"]["sections"]["filters"],
    skills["trace"]["sections"]["related_skills"],
]
trace_no_hints = without_related_skills(trace_curated)

# Trace: all sections (for ALL_SECTIONS treatment only)
trace_all = skills["trace"]["all"]

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
            "langsmith-trace": skill_config(trace_curated, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=basic_validators(),
    ),
    # Both: Workflow rules in CLAUDE.md AND skill hints (reinforcement)
    "BASIC_BOTH": Treatment(
        description="Workflow rules in CLAUDE.md AND skill hints",
        skills={
            "langsmith-trace": skill_config(trace_curated, skills["trace"]["scripts_dir"]),
            "langsmith-dataset": skill_config(dataset_curated, skills["dataset"]["scripts_dir"]),
        },
        claude_md=CLAUDE_MD_WORKFLOW_BASIC,
        validators=basic_validators(),
    ),
    # All sections: Complete skill content (without cross-skill hints) + full CLAUDE.md sample
    "BASIC_ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={
            "langsmith-trace": skill_config(
                without_related_skills(skills["trace"]["all"]), skills["trace"]["scripts_dir"]
            ),
            "langsmith-dataset": skill_config(
                without_related_skills(skills["dataset"]["all"]), skills["dataset"]["scripts_dir"]
            ),
        },
        claude_md=CLAUDE_FULL,
        validators=basic_validators(),
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
    prompt = BASIC_PROMPT_TEMPLATE.format(run_id=dataset_name)
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
