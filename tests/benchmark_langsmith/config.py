"""LangSmith Synergy experiment configuration.

Shared utilities for test_basic.py and test_advanced.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    MetricsCollector,
    SkillInvokedValidator,
)
from skills.parser import load_skill
from tests.benchmark_langsmith.validation.validators import (
    DatasetStructureValidator,
    EvaluatorValidator,
    SkillScriptValidator,
    TrajectoryAccuracyValidator,
)

# =============================================================================
# SKILL LOADING
# =============================================================================

SKILL_BASE = Path(__file__).parent.parent.parent / "skills" / "benchmarks"


def load_skills():
    """Load all skills from skill.md files."""
    return {
        "trace": load_skill(SKILL_BASE / "langsmith_trace"),
        "dataset": load_skill(SKILL_BASE / "langsmith_dataset"),
        "evaluator": load_skill(SKILL_BASE / "langsmith_evaluator"),
    }


skills = load_skills()


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
# CLAUDE.MD VARIANTS
# =============================================================================

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

CLAUDE_MD_SKILLS_ONLY = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.
"""

CLAUDE_MD_WORKFLOW_BASIC = CLAUDE_MD_SKILLS_ONLY + "\n" + WORKFLOW_RULE_BASIC
CLAUDE_MD_WORKFLOW_ADVANCED = CLAUDE_MD_SKILLS_ONLY + "\n" + WORKFLOW_RULE_ADVANCED


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

BASIC_PROMPT_TEMPLATE = """Create a trajectory dataset with 5 examples from the 5 most recent traces in our LangSmith project.

Output: trajectory_dataset.json (upload as "{run_id}" to LangSmith)

Run any code you write directly."""

ADVANCED_PROMPT_TEMPLATE = """Create a trajectory dataset with 5 examples from the 5 most recent traces in our LangSmith project, plus an evaluator measuring tool call match percentage.

Output: trajectory_dataset.json and trajectory_evaluator.py (upload both as "{run_id}" to LangSmith)

Run any code you write directly."""


# =============================================================================
# VALIDATOR FACTORIES
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


def advanced_validators():
    """Validators for advanced test (trace + dataset + evaluator)."""
    return [
        SkillInvokedValidator("langsmith-trace", required=False),
        SkillInvokedValidator("langsmith-dataset", required=False),
        SkillInvokedValidator("langsmith-evaluator", required=False),
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
        EvaluatorValidator(
            filename="trajectory_evaluator.py",
            verify_upload=True,
            upload_prefix="test-",
        ),
        MetricsCollector(),
    ]


# =============================================================================
# ENVIRONMENT CONFIG
# =============================================================================

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt"]
