"""Generic test runner for task + treatment combinations.

This test file uses the new task-based structure where:
- Tasks are self-contained directories with instruction.md, task.toml, environment/, validation/
- Treatments are defined in treatments.yaml and specify skill configurations
- Any treatment can be combined with any compatible task

Usage:
    # Run all task/treatment combinations
    pytest tests/test_tasks.py -v

    # Run specific task
    pytest tests/test_tasks.py -k "ls-evaluator" -v

    # Run specific treatment
    pytest tests/test_tasks.py -k "SEPARATE_NAMES" -v

    # Run specific combination
    pytest tests/test_tasks.py -k "ls-evaluator and UNIFIED_BOTH" -v
"""

import uuid
from pathlib import Path

import pytest

from scaffold import Treatment
from scaffold.python import extract_events, parse_output
from scaffold.tasks import load_task
from scaffold.treatments import build_treatment_skills, load_treatments_yaml

# Timeouts
CLAUDE_TIMEOUT = 600  # 10 minutes for Claude to complete task
PYTEST_TIMEOUT = 900  # 15 minutes total including setup/teardown

# Task -> compatible treatments mapping
TASK_TREATMENTS = {
    "ls-evaluator": [
        "SEPARATE_NAMES",
        "UNIFIED_BOTH",
        "UNIFIED_WITH_NOISE",
        "UNIFIED_PY_ONLY",
        "UNIFIED_TS_ONLY",
        "CONTROL",
    ],
    "ls-tracing": [
        "SEPARATE_NAMES",
        "UNIFIED_BOTH",
        "UNIFIED_WITH_NOISE",
        "UNIFIED_PY_ONLY",
        "UNIFIED_TS_ONLY",
        "CONTROL",
    ],
    "ls-multiskill-basic": [
        "MULTISKILL_ALL_SKILLS",
        "MULTISKILL_SKILLS_ONLY",
        "MULTISKILL_CLAUDEMD_ONLY",
        "CONTROL",
    ],
    "ls-multiskill-advanced": [
        "MULTISKILL_ALL_SKILLS",
        "MULTISKILL_SKILLS_ONLY",
        "MULTISKILL_CLAUDEMD_ONLY",
        "CONTROL",
    ],
}


def generate_test_params():
    """Generate (task_name, treatment_name) pairs for parametrization."""
    params = []
    for task_name, treatments in TASK_TREATMENTS.items():
        for treatment_name in treatments:
            params.append((task_name, treatment_name))
    return params


def run_validators(validators: list, test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run function-based validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in validators:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed


@pytest.mark.timeout(PYTEST_TIMEOUT)
@pytest.mark.parametrize("task_name,treatment_name", generate_test_params())
def test_task_treatment(
    task_name,
    treatment_name,
    # Fixtures from conftest
    verify_environment,
    langsmith_project,
    test_dir,
    setup_test_context,
    run_claude,
    record_result,
):
    """Run a task with a treatment and validate results."""
    # Load task and treatment
    task = load_task(task_name)
    treatment_configs = load_treatments_yaml()
    treatment_cfg = treatment_configs[treatment_name]

    # Load validators from task
    validators = task.load_validators()

    # Build treatment
    skills = build_treatment_skills(treatment_cfg.skills) if treatment_cfg.skills else {}

    treatment = Treatment(
        description=treatment_cfg.description,
        skills=skills,
        claude_md=treatment_cfg.claude_md if treatment_cfg.claude_md else None,
        validators=[],  # We use function-based validators directly
    )

    # Setup test context with task's environment
    setup_test_context(
        skills=treatment.skills,
        claude_md=treatment.claude_md,
        environment_dir=task.environment_dir,
    )

    # Generate run_id for parallel execution
    run_id = str(uuid.uuid4())

    # Render prompt with required variables
    template_vars = {"run_id": run_id}

    # Add task-specific variables (e.g., datasets for ls-evaluator)
    if task_name == "ls-evaluator":
        # These would come from fixtures in a real test
        template_vars["py_dataset"] = f"benchmark-sql-{run_id[:8]}"
        template_vars["ts_dataset"] = f"benchmark-support-{run_id[:8]}"

    prompt = task.render_prompt(**template_vars)
    prompt = treatment.build_prompt(prompt)

    # Run Claude
    result = run_claude(prompt, timeout=CLAUDE_TIMEOUT)

    # Parse output
    events = extract_events(parse_output(result.stdout))

    # Run validators
    outputs = {"run_id": run_id, "langsmith_project": langsmith_project}
    passed, failed = run_validators(validators, test_dir, outputs)

    # Record results
    record_result(events, passed, failed, run_id=run_id)

    assert not failed, f"Validation failed: {failed}"
