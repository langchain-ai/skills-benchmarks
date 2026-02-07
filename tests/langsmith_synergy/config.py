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
)
from skill_constructs.langchain.langsmith_dataset.skill import (
    DEFAULT_SECTIONS as DATASET_SECTIONS,
)
from skill_constructs.langchain.langsmith_evaluator.skill import (
    DEFAULT_SECTIONS as EVALUATOR_SECTIONS,
)
from tests.langsmith_synergy.validators import (
    DatasetValidator,
    EvaluatorValidator,
    TraceDataValidator,
    LangSmithAPIValidator,
    SkillScriptValidator,
    LangSmithDatasetValidator,
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

Dependencies:
- Datasets require trace data (use trace skill to get data first)
- Evaluators are designed to work with datasets (create dataset before evaluator)"""

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

def skill_without_workflow(sections):
    """Remove the Next Steps section from skill sections."""
    return [s for s in sections if s and "Next Steps" not in s]


def skill_config(sections, scripts_dir=None):
    """Create skill config with sections and optional scripts directory."""
    return {"sections": sections, "scripts_dir": scripts_dir}


# Standard skills (include Next Steps with workflow hints) + scripts
TRACE_SKILL_STANDARD = skill_config(TRACE_SECTIONS, TRACE_SCRIPTS_DIR)
DATASET_SKILL_STANDARD = skill_config(DATASET_SECTIONS, DATASET_SCRIPTS_DIR)
EVALUATOR_SKILL_STANDARD = skill_config(EVALUATOR_SECTIONS, EVALUATOR_SCRIPTS_DIR)

# Skills without workflow hints + scripts
TRACE_SKILL_NO_WORKFLOW = skill_config(skill_without_workflow(TRACE_SECTIONS), TRACE_SCRIPTS_DIR)
DATASET_SKILL_NO_WORKFLOW = skill_config(skill_without_workflow(DATASET_SECTIONS), DATASET_SCRIPTS_DIR)
EVALUATOR_SKILL_NO_WORKFLOW = skill_config(skill_without_workflow(EVALUATOR_SECTIONS), EVALUATOR_SCRIPTS_DIR)


# =============================================================================
# PROMPTS
# =============================================================================

# Basic test prompt: Query traces and generate a dataset
BASIC_PROMPT = """Query 5 traces from the LangSmith project (use LANGSMITH_PROJECT env variable) and generate a trajectory dataset with 5 examples.

Steps:
1. Query 5 recent traces from the project
2. Generate a trajectory dataset from those traces (5 examples)
3. Save to trajectory_dataset.json

The sql_agent.py has been run and traces exist in LangSmith.

IMPORTANT: If you create any files, run them directly (not in background). If code fails, you have 2 attempts to fix it."""

# Advanced test prompt: Full pipeline
ADVANCED_PROMPT = """Query 5 traces from the LangSmith project, generate a trajectory dataset (5 examples), and create an evaluator.

Steps:
1. Query 5 recent traces from the project
2. Generate a trajectory dataset (5 examples)
3. Create a trajectory evaluator that validates tool call sequences
4. Save:
   - Dataset to trajectory_dataset.json
   - Evaluator to trajectory_evaluator.py

The sql_agent.py has been run and traces exist in LangSmith.

IMPORTANT: If you create any files, run them directly (not in background). If code fails, you have 2 attempts to fix it."""


# =============================================================================
# VALIDATORS
# =============================================================================

def basic_validators():
    """Validators for basic test (trace + dataset)."""
    return [
        # Skill invocation tracking
        SkillInvokedValidator("langsmith-trace", required=False),
        SkillInvokedValidator("langsmith-dataset", required=False),

        # Skill script usage validation
        SkillScriptValidator({
            "query_traces.py": "query_traces.py",
            "generate_datasets.py": "generate_datasets.py",
        }),

        # LangSmith API validation - verify traces actually exist
        LangSmithAPIValidator(
            min_traces=1,
            max_age_minutes=1440,  # 24 hours
            require_tool_calls=True,
        ),

        # Trace data validation - verify meaningful trace data was retrieved
        TraceDataValidator(
            require_hierarchy=True,
            min_traces=1,
        ),

        # Dataset validation - strict trajectory structure checks
        DatasetValidator(
            filename="trajectory_dataset.json",
            min_examples=1,
            dataset_type="trajectory",
        ),

        # LangSmith dataset validation - check if uploaded
        LangSmithDatasetValidator(
            dataset_name_pattern="trajectory",
            min_examples=1,
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

        # Skill script usage validation
        SkillScriptValidator({
            "query_traces.py": "query_traces.py",
            "generate_datasets.py": "generate_datasets.py",
        }),

        # LangSmith API validation - verify traces actually exist
        LangSmithAPIValidator(
            min_traces=1,
            max_age_minutes=1440,  # 24 hours
            require_tool_calls=True,
        ),

        # Trace data validation - verify meaningful trace data was retrieved
        TraceDataValidator(
            require_hierarchy=True,
            min_traces=1,
        ),

        # Dataset validation - strict trajectory structure checks
        DatasetValidator(
            filename="trajectory_dataset.json",
            min_examples=1,
            dataset_type="trajectory",
        ),

        # LangSmith dataset validation - check if uploaded
        LangSmithDatasetValidator(
            dataset_name_pattern="trajectory",
            min_examples=1,
        ),

        # Evaluator validation - strict code quality checks for trajectory evaluators
        EvaluatorValidator(
            filename="trajectory_evaluator.py",
            evaluator_type="trajectory",
        ),

        # Metrics
        MetricsCollector(),
    ]


# =============================================================================
# TREATMENTS - BASIC (2 skills: trace + dataset)
# =============================================================================

BASIC_TREATMENTS = {
    # Baseline: Skills only, no CLAUDE.md
    "BASIC_BASELINE": Treatment(
        description="Skills with workflow hints, no CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
        },
        validators=basic_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "BASIC_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": TRACE_SKILL_NO_WORKFLOW,
            "langsmith-dataset": DATASET_SKILL_NO_WORKFLOW,
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
}


# =============================================================================
# TREATMENTS - ADVANCED (3 skills: trace + dataset + evaluator)
# =============================================================================

ADVANCED_TREATMENTS = {
    # Baseline: Skills only, no CLAUDE.md
    "ADV_BASELINE": Treatment(
        description="Skills with workflow hints, no CLAUDE.md",
        skills={
            "langsmith-trace": TRACE_SKILL_STANDARD,
            "langsmith-dataset": DATASET_SKILL_STANDARD,
            "langsmith-evaluator": EVALUATOR_SKILL_STANDARD,
        },
        validators=advanced_validators(),
    ),

    # CLAUDE.md only: Workflow rules in CLAUDE.md, skills without hints
    "ADV_CLAUDEMD": Treatment(
        description="Workflow rules in CLAUDE.md, skills without hints",
        skills={
            "langsmith-trace": TRACE_SKILL_NO_WORKFLOW,
            "langsmith-dataset": DATASET_SKILL_NO_WORKFLOW,
            "langsmith-evaluator": EVALUATOR_SKILL_NO_WORKFLOW,
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
}

# Combined treatments dict
TREATMENTS = {**BASIC_TREATMENTS, **ADVANCED_TREATMENTS}


# =============================================================================
# PROMPT BUILDERS
# =============================================================================

def build_basic_prompt(treatment: Treatment, treatment_name: str = None) -> str:
    """Build prompt for basic test."""
    return treatment.build_prompt(BASIC_PROMPT)


def build_advanced_prompt(treatment: Treatment, treatment_name: str = None) -> str:
    """Build prompt for advanced test."""
    return treatment.build_prompt(ADVANCED_PROMPT)


def build_prompt(treatment: Treatment, treatment_name: str = None) -> str:
    """Build prompt based on treatment type."""
    if treatment_name and treatment_name.startswith("ADV_"):
        return build_advanced_prompt(treatment, treatment_name)
    return build_basic_prompt(treatment, treatment_name)


# =============================================================================
# PRESETS
# =============================================================================

BASIC_COMPARISON = list(BASIC_TREATMENTS.keys())
ADVANCED_COMPARISON = list(ADVANCED_TREATMENTS.keys())
ALL_TREATMENTS_LIST = list(TREATMENTS.keys())
