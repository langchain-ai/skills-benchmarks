"""LangSmith Synergy experiment.

Tests whether Claude can use multiple skills together effectively.
Two test scenarios:
1. Basic: langsmith-trace + langsmith-dataset (2 skills)
2. Advanced: langsmith-trace + langsmith-dataset + langsmith-evaluator (3 skills)

Treatments test where workflow rules should be defined:
- In CLAUDE.md only
- In skills only (via "Next Steps" sections)
- In both (reinforcement)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    Treatment,
    SkillInvokedValidator,
    MetricsCollector,
)
from skill_constructs.langchain.langsmith_trace.skill import (
    DEFAULT_SECTIONS as TRACE_SECTIONS,
    FULL_SECTIONS as TRACE_FULL_SECTIONS,
)
from skill_constructs.langchain.langsmith_dataset.skill import (
    DEFAULT_SECTIONS as DATASET_SECTIONS,
    FULL_SECTIONS as DATASET_FULL_SECTIONS,
)
from skill_constructs.langchain.langsmith_evaluator.skill import (
    DEFAULT_SECTIONS as EVALUATOR_SECTIONS,
    FULL_SECTIONS as EVALUATOR_FULL_SECTIONS,
)
from skill_constructs import CLAUDE_SAMPLE
from tests.langsmith_synergy.validation.validators import (
    DatasetValidator,
    EvaluatorValidator,
    TraceDataValidator,
    SkillScriptValidator,
)

# Scripts directories (from skill_constructs)
SKILL_CONSTRUCTS_BASE = Path(__file__).parent.parent.parent / "skill_constructs" / "langchain"
TRACE_SCRIPTS_DIR = SKILL_CONSTRUCTS_BASE / "langsmith_trace" / "scripts"
DATASET_SCRIPTS_DIR = SKILL_CONSTRUCTS_BASE / "langsmith_dataset" / "scripts"
EVALUATOR_SCRIPTS_DIR = SKILL_CONSTRUCTS_BASE / "langsmith_evaluator" / "scripts"


# =============================================================================
# WORKFLOW RULES (for CLAUDE.md and skill variations)
# =============================================================================

# Workflow rule to add to CLAUDE.md
WORKFLOW_RULE_BASIC = """## LangSmith Skills

This project has LangSmith skills for working with traces and datasets:

- **langsmith-trace**: Query and analyze traces from LangSmith projects
- **langsmith-dataset**: Generate datasets from trace data

Note: The dataset skill requires trace data to work with. Use the trace skill first to understand available data before generating datasets."""

WORKFLOW_RULE_ADVANCED = """## LangSmith Skills

This project has LangSmith skills for working with traces, datasets, and evaluators:

- **langsmith-trace**: Query and analyze traces from LangSmith projects
- **langsmith-dataset**: Generate datasets from trace data
- **langsmith-evaluator**: Create evaluators for validating agent outputs

Workflow:
- Datasets require trace data (use trace skill to get data first)
- Evaluators validate datasets (create dataset before evaluator)
- Evaluators should use the same field structure as your dataset (e.g., if dataset has `expected_trajectory`, evaluator should read that field)"""

# Base CLAUDE.md that just mentions skills exist
CLAUDE_MD_SKILLS_ONLY = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
"""

# CLAUDE.md with workflow rules for basic test
CLAUDE_MD_WORKFLOW_BASIC = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.

""" + WORKFLOW_RULE_BASIC

# CLAUDE.md with workflow rules for advanced test
CLAUDE_MD_WORKFLOW_ADVANCED = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.

""" + WORKFLOW_RULE_ADVANCED

# =============================================================================
# SKILL VARIATIONS
# =============================================================================

def skill_without_hints(sections):
    """Remove the Related Skills section from skill sections."""
    return [s for s in sections if s and "Related Skills" not in s]


def skill_config(sections, scripts_dir=None):
    """Create skill config with sections and optional scripts directory."""
    return {"sections": sections, "scripts_dir": scripts_dir}


# Standard skills (include Next Steps with workflow hints) + scripts
TRACE_SKILL_STANDARD = skill_config(TRACE_SECTIONS, TRACE_SCRIPTS_DIR)
DATASET_SKILL_STANDARD = skill_config(DATASET_SECTIONS, DATASET_SCRIPTS_DIR)
EVALUATOR_SKILL_STANDARD = skill_config(EVALUATOR_SECTIONS, EVALUATOR_SCRIPTS_DIR)

# Skills without workflow hints + scripts
TRACE_SKILL_NO_HINTS = skill_config(skill_without_hints(TRACE_SECTIONS), TRACE_SCRIPTS_DIR)
DATASET_SKILL_NO_HINTS = skill_config(skill_without_hints(DATASET_SECTIONS), DATASET_SCRIPTS_DIR)
EVALUATOR_SKILL_NO_HINTS = skill_config(skill_without_hints(EVALUATOR_SECTIONS), EVALUATOR_SCRIPTS_DIR)

# Full skills (all sections) + scripts
TRACE_SKILL_FULL = skill_config(TRACE_FULL_SECTIONS, TRACE_SCRIPTS_DIR)
DATASET_SKILL_FULL = skill_config(DATASET_FULL_SECTIONS, DATASET_SCRIPTS_DIR)
EVALUATOR_SKILL_FULL = skill_config(EVALUATOR_FULL_SECTIONS, EVALUATOR_SCRIPTS_DIR)


# =============================================================================
# PROMPTS
# =============================================================================

# Basic test prompt template - {run_id} will be replaced with unique identifier
BASIC_PROMPT_TEMPLATE = """I need to evaluate whether my agent is using the right tools. Build me a dataset from the LangSmith project in .env that captures the expected tool sequences.

- Include 5 traces
- Output: trajectory_dataset.json (also upload as "test-{run_id}")

Run any code you write directly."""

# Advanced test prompt template - {run_id} will be replaced with unique identifier
ADVANCED_PROMPT_TEMPLATE = """I want to test if my agent calls tools correctly. Create a dataset and an evaluator from the LangSmith project in .env.

- Include 5 traces
- Dataset: trajectory_dataset.json (upload to LangSmith as "test-{run_id}")
- Evaluator: trajectory_evaluator.py (upload to LangSmith as "test-{run_id}", attached to our dataset)

Run any code you write directly."""


# =============================================================================
# VALIDATORS
# =============================================================================

def basic_validators():
    """Validators for basic test (trace + dataset)."""
    return [
        # Skill invocation tracking
        SkillInvokedValidator("langsmith-trace", required=False),
        SkillInvokedValidator("langsmith-dataset", required=False),

        # Skill script usage
        SkillScriptValidator({
            "query_traces.py": "query_traces.py",
            "generate_datasets.py": "generate_datasets.py",
        }),

        # Trace validation (includes API check)
        TraceDataValidator(min_traces=1),

        # Dataset validation
        DatasetValidator(
            filename="trajectory_dataset.json",
            min_examples=1,
            dataset_type="trajectory",
        ),

        # Metrics
        MetricsCollector(),
    ]


def advanced_validators():
    """Validators for advanced test (trace + dataset + evaluator)."""
    return [
        # Skill invocation tracking
        SkillInvokedValidator("langsmith-trace", required=False),
        SkillInvokedValidator("langsmith-dataset", required=False),
        SkillInvokedValidator("langsmith-evaluator", required=False),

        # Skill script usage
        SkillScriptValidator({
            "query_traces.py": "query_traces.py",
            "generate_datasets.py": "generate_datasets.py",
        }),

        # Trace validation (includes API check)
        TraceDataValidator(min_traces=1),

        # Dataset validation
        DatasetValidator(
            filename="trajectory_dataset.json",
            min_examples=1,
            dataset_type="trajectory",
        ),

        # Evaluator validation (uses test cases from ground truth)
        EvaluatorValidator(
            filename="trajectory_evaluator.py",
            verify_upload=True,
            upload_prefix="test-",
        ),

        # Metrics
        MetricsCollector(),
    ]


# =============================================================================
# TREATMENTS - BASIC (2 skills: trace + dataset)
# =============================================================================

BASIC_TREATMENTS = {
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
            "langsmith-trace": TRACE_SKILL_NO_HINTS,
            "langsmith-dataset": DATASET_SKILL_NO_HINTS,
        },
        validators=basic_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "BASIC_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": TRACE_SKILL_NO_HINTS,
            "langsmith-dataset": DATASET_SKILL_NO_HINTS,
        },
        claude_md=CLAUDE_MD_WORKFLOW_BASIC,
        validators=basic_validators(),
    ),

    # Skills only: Workflow hints in skills, minimal CLAUDE.md
    "BASIC_SKILLS": Treatment(
        description="Workflow hints in skills, minimal CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
        },
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=basic_validators(),
    ),

    # Both: Workflow rules in CLAUDE.md AND skill hints (reinforcement)
    "BASIC_BOTH": Treatment(
        description="Workflow rules in CLAUDE.md AND skill hints",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
        },
        claude_md=CLAUDE_MD_WORKFLOW_BASIC,
        validators=basic_validators(),
    ),

    # All sections: Complete skill content + full CLAUDE.md sample
    "BASIC_ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_FULL,
            "langsmith-dataset": DATASET_SKILL_FULL,
        },
        claude_md=CLAUDE_SAMPLE,
        validators=basic_validators(),
    ),
}


# =============================================================================
# TREATMENTS - ADVANCED (3 skills: trace + dataset + evaluator)
# =============================================================================

ADVANCED_TREATMENTS = {
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
            "langsmith-trace": TRACE_SKILL_NO_HINTS,
            "langsmith-dataset": DATASET_SKILL_NO_HINTS,
            "langsmith-evaluator": EVALUATOR_SKILL_NO_HINTS,
        },
        validators=advanced_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "ADV_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": TRACE_SKILL_NO_HINTS,
            "langsmith-dataset": DATASET_SKILL_NO_HINTS,
            "langsmith-evaluator": EVALUATOR_SKILL_NO_HINTS,
        },
        claude_md=CLAUDE_MD_WORKFLOW_ADVANCED,
        validators=advanced_validators(),
    ),

    # Skills only: Workflow hints in skills, minimal CLAUDE.md
    "ADV_SKILLS": Treatment(
        description="Workflow hints in skills, minimal CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
            "langsmith-evaluator": EVALUATOR_SKILL_STANDARD,
        },
        claude_md=CLAUDE_MD_SKILLS_ONLY,
        validators=advanced_validators(),
    ),

    # Both: Workflow rules in CLAUDE.md AND skill hints (reinforcement)
    "ADV_BOTH": Treatment(
        description="Workflow rules in CLAUDE.md AND skill hints",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
            "langsmith-evaluator": EVALUATOR_SKILL_STANDARD,
        },
        claude_md=CLAUDE_MD_WORKFLOW_ADVANCED,
        validators=advanced_validators(),
    ),

    # All sections: Complete skill content + full CLAUDE.md sample
    "ADV_ALL_SECTIONS": Treatment(
        description="All skill sections + full CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_FULL,
            "langsmith-dataset": DATASET_SKILL_FULL,
            "langsmith-evaluator": EVALUATOR_SKILL_FULL,
        },
        claude_md=CLAUDE_SAMPLE,
        validators=advanced_validators(),
    ),
}

# Combined treatments dict
TREATMENTS = {**BASIC_TREATMENTS, **ADVANCED_TREATMENTS}


# =============================================================================
# PROMPT BUILDERS
# =============================================================================

from datetime import datetime

def _get_dataset_name(treatment_name: str, rep: int = 1) -> str:
    """Generate unique dataset name: treatment-repN-YYYYMMDD-HHMMSS."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    prefix = treatment_name.lower().replace("_", "-") if treatment_name else "test"
    return f"{prefix}-rep{rep}-{timestamp}"


def build_basic_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1) -> str:
    """Build prompt for basic test."""
    dataset_name = _get_dataset_name(treatment_name, rep)
    prompt = BASIC_PROMPT_TEMPLATE.format(run_id=dataset_name)
    return treatment.build_prompt(prompt)


def build_advanced_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1) -> str:
    """Build prompt for advanced test."""
    dataset_name = _get_dataset_name(treatment_name, rep)
    prompt = ADVANCED_PROMPT_TEMPLATE.format(run_id=dataset_name)
    return treatment.build_prompt(prompt)


def build_prompt(treatment: Treatment, treatment_name: str = None, rep: int = 1) -> str:
    """Build prompt based on treatment type."""
    if treatment_name and treatment_name.startswith("ADV_"):
        return build_advanced_prompt(treatment, treatment_name, rep)
    return build_basic_prompt(treatment, treatment_name, rep)


# =============================================================================
# PRESETS
# =============================================================================

BASIC_COMPARISON = list(BASIC_TREATMENTS.keys())
ADVANCED_COMPARISON = list(ADVANCED_TREATMENTS.keys())
ALL_TREATMENTS_LIST = list(TREATMENTS.keys())

# All sections vs control
BASIC_ALL_SECTIONS_VS_CONTROL = ["BASIC_CONTROL", "BASIC_ALL_SECTIONS"]
ADV_ALL_SECTIONS_VS_CONTROL = ["ADV_CONTROL", "ADV_ALL_SECTIONS"]
