"""LangSmith evaluator benchmark - language-specific vs unified skills.

Tests whether separate skill names (langsmith-evaluator-py, langsmith-evaluator-js) help
Claude create evaluators in the correct language for each agent type.

Run with: pytest tests/benchmarks/ls_languages/test_evaluators.py -v
Parallel:  pytest tests/benchmarks/ls_languages/test_evaluators.py -n 4
"""

import re
import uuid
from pathlib import Path

import pytest

from scaffold import MetricsCollector, Treatment
from scaffold.python import extract_events, parse_output
from skills.parser import load_skill_variant, skill_config
from tests.benchmarks.helpers import CLAUDE_TIMEOUT, PYTEST_TIMEOUT
from tests.benchmarks.ls_languages.validation.validators import (
    LanguageValidator,
    DatasetValidator,
    SyntaxValidator,
    UploadValidator,
)

SKILL_BASE = Path(__file__).parent.parent.parent.parent / "skills" / "benchmarks"

CLAUDE_MD_GENERIC = """# Project Guidelines

Before starting any coding task, check available project skills to find the best approach.

## General Principles

- **Understand before building**: Query and inspect existing data structures before writing code that processes them
- **Match schemas exactly**: Code should access the exact field names present in the data, not assumed names
- **Use skill scripts**: Reference the scripts in skills for working patterns
"""


def _add_language_suffix(content: str, lang: str) -> str:
    """Add language suffix to frontmatter description."""
    suffix = "(Python)" if lang == "py" else "(TypeScript)"
    return re.sub(
        r'^(description: "?)(.+?)("?)$',
        rf"\1\2 {suffix}\3",
        content, count=1, flags=re.MULTILINE
    )


def _filter_related_skills(sections: list[str]) -> list[str]:
    """Filter out related_skills sections (cross-skill references for multiskill tests)."""
    return [s for s in sections if s and "<related_skills>" not in s]


def _load_skill(name: str, variant: str, lang_suffix: str | None = None) -> dict:
    skill = load_skill_variant(SKILL_BASE / name, variant)
    sections = _filter_related_skills(skill["all"])
    content = "\n\n".join(sections)
    if lang_suffix:
        content = _add_language_suffix(content, lang_suffix)
    return skill_config([content], skill["scripts_dir"], skill["script_filter"])


def _load_noise_skill() -> dict | None:
    skill_path = SKILL_BASE / "langchain_basic"
    if (skill_path / "skill.md").exists():
        return skill_config([(skill_path / "skill.md").read_text()], None, None)
    return None


def _build_separate_skills() -> dict:
    skills = {}
    for skill_type in ["trace", "evaluator", "dataset"]:
        skills[f"langsmith-{skill_type}-py"] = _load_skill(f"langsmith_{skill_type}", "py", "py")
        skills[f"langsmith-{skill_type}-ts"] = _load_skill(f"langsmith_{skill_type}", "ts", "ts")
    if noise := _load_noise_skill():
        skills["langchain-basic"] = noise
    return skills


def _build_unified_skills(variant: str, include_others: bool = True, add_noise: bool = False) -> dict:
    skills = {"langsmith-evaluator": _load_skill("langsmith_evaluator", variant)}
    if include_others:
        for skill_type in ["trace", "dataset"]:
            skills[f"langsmith-{skill_type}"] = _load_skill(f"langsmith_{skill_type}", variant)
    if add_noise and (noise := _load_noise_skill()):
        skills["langchain-basic"] = noise
    return skills


TASK_PROMPT_TEMPLATE = """We've collected LangSmith datasets for each agent in this full-stack project:
- Backend SQL Agent: `{py_dataset}` (trajectory dataset)
- Frontend Support Bot: `{ts_dataset}` (final_response dataset)

Create evaluators to score the agents. These evaluators will be attached to the LangSmith datasets, so they have a dependency on the datasets structure.

1. For the backend SQL agent (`backend/sql_agent.py`):
   - Create a trajectory evaluator that compares the tool calls made by the agent to the expected_trajectory in the dataset.
   - The evaluator should be named `evaluator` with an appropriate file extension.
   - Upload the evaluator to the LangSmith dataset with name `test-be-{run_id}`.

2. For the frontend support bot (`frontend/support_bot.ts`):
   - Create a final_response evaluator that compares answer from our bot to the expected response in the dataset.
   - The evaluator should be named `evaluator` with an appropriate file extension.
   - Upload the evaluator to the LangSmith dataset with name `test-fe-{run_id}`.
"""

VALIDATORS = [
    LanguageValidator(),
    SyntaxValidator(),
    DatasetValidator(),  # Tests against real traced datasets
    UploadValidator(),
    MetricsCollector(),
]

TREATMENTS = {
    "SEPARATE_NAMES": Treatment(
        description="Language-specific skill names (evaluator-py/ts, trace-py/ts, dataset-py/ts + noise)",
        skills=_build_separate_skills(),
        claude_md=CLAUDE_MD_GENERIC,
        validators=VALIDATORS,
    ),
    "UNIFIED_BOTH": Treatment(
        description="Unified skills (evaluator/trace/dataset with all variants)",
        skills=_build_unified_skills("all", include_others=True),
        claude_md=CLAUDE_MD_GENERIC,
        validators=VALIDATORS,
    ),
    "UNIFIED_WITH_NOISE": Treatment(
        description="Unified skills + distractor noise skill",
        skills=_build_unified_skills("all", include_others=True, add_noise=True),
        claude_md=CLAUDE_MD_GENERIC,
        validators=VALIDATORS,
    ),
    "UNIFIED_PY_ONLY": Treatment(
        description="Single skill with only Python content",
        skills=_build_unified_skills("py", include_others=False),
        claude_md=CLAUDE_MD_GENERIC,
        validators=VALIDATORS,
    ),
    "UNIFIED_TS_ONLY": Treatment(
        description="Single skill with only TypeScript content",
        skills=_build_unified_skills("ts", include_others=False),
        claude_md=CLAUDE_MD_GENERIC,
        validators=VALIDATORS,
    ),
    "CONTROL": Treatment(
        description="No skills (baseline - Claude's native knowledge)",
        skills={},
        validators=VALIDATORS,
    ),
}


@pytest.mark.timeout(PYTEST_TIMEOUT)
@pytest.mark.parametrize("treatment_name", list(TREATMENTS.keys()))
def test_treatment(
    treatment_name,
    verify_environment,
    langsmith_project,
    langsmith_dataset,
    test_dir,
    setup_test_context,
    run_claude,
    record_result,
    environment_dir,
):
    """Test a single treatment."""
    treatment = TREATMENTS[treatment_name]

    setup_test_context(
        skills=treatment.skills,
        claude_md=treatment.claude_md,
        environment_dir=environment_dir,
    )

    run_id = str(uuid.uuid4())
    task_prompt = TASK_PROMPT_TEMPLATE.format(
        py_dataset=langsmith_dataset["py"],
        ts_dataset=langsmith_dataset["ts"],
        run_id=run_id,
    )
    prompt = treatment.build_prompt(task_prompt)

    result = run_claude(prompt, timeout=CLAUDE_TIMEOUT)

    events = extract_events(parse_output(result.stdout))
    outputs = {"run_id": run_id, "langsmith_project": langsmith_project}
    passed, failed = treatment.validate(events, test_dir, outputs)

    record_result(events, passed, failed, run_id=run_id)
    assert not failed, f"Validation failed: {failed}"
