"""Generic test runner for task + treatment combinations.

This test file uses the task-based structure where:
- Tasks are self-contained directories with instruction.md, task.toml, environment/, validation/
- Treatments are shared across tasks in treatments/{category}/*.yaml
- Any treatment can be used with any task

Usage:
    # Run all default task/treatment combinations
    pytest tests/tasks/test_tasks.py -v

    # Run specific task with specific treatment
    pytest tests/tasks/test_tasks.py --task=ls-evaluator --treatment=LS_BASIC_PY -v

    # Run specific task with multiple treatments (comma-separated)
    pytest tests/tasks/test_tasks.py --task=ls-evaluator --treatment=LS_BASIC_PY,LS_WORKFLOW_PY -v

    # Run specific task with all its default treatments
    pytest tests/tasks/test_tasks.py --task=ls-evaluator -v

    # Run specific treatment across all tasks that have it as default
    pytest tests/tasks/test_tasks.py --treatment=CONTROL -v

    # Run with repetitions and parallel workers
    pytest tests/tasks/test_tasks.py --task=ls-evaluator --treatment=CONTROL --count=2 -n 2 -v

    # Run with wildcard pattern (matches all treatments starting with prefix)
    pytest tests/tasks/test_tasks.py --task=ls-evaluator --treatment=LS_BASIC_* -v
"""

import os
import uuid
from pathlib import Path

import pytest
from langsmith import testing as ls_testing

from scaffold import NoiseTask, Treatment
from scaffold.python import extract_events, parse_output
from scaffold.python.tasks import list_tasks, load_task
from scaffold.python.treatments import build_treatment_skills, load_treatments
from scaffold.python.validation import NOISE_TASK_DELIVERABLES, NOISE_TASK_PROMPTS


def build_noise_tasks(noise_task_names: list[str]) -> list[NoiseTask]:
    """Convert noise task names to NoiseTask objects."""
    noise_tasks = []
    for name in noise_task_names:
        if name in NOISE_TASK_PROMPTS:
            noise_tasks.append(
                NoiseTask(
                    prompt=NOISE_TASK_PROMPTS[name],
                    deliverables=[NOISE_TASK_DELIVERABLES.get(name, "")],
                )
            )
    return noise_tasks


# Timeouts
CLAUDE_TIMEOUT = 600  # 10 minutes for Claude to complete task
PYTEST_TIMEOUT = 900  # 15 minutes total including setup/teardown


def expand_treatment_patterns(patterns: list[str], all_treatments: dict) -> list[str]:
    """Expand treatment patterns into matching treatment names.

    Supports:
    - Exact names: "LS_BASIC_PY"
    - Wildcards: "LS_BASIC_*" (matches LS_BASIC_PY, LS_BASIC_TS, etc.)
    """
    treatment_names = list(all_treatments.keys())
    expanded = []

    for pattern in patterns:
        if pattern.endswith("*"):
            # Wildcard pattern - match prefix
            prefix = pattern[:-1]
            matches = [t for t in treatment_names if t.startswith(prefix)]
            if not matches:
                raise ValueError(
                    f"No treatments match pattern: {pattern}. Available: {treatment_names}"
                )
            expanded.extend(matches)
        else:
            # Exact match
            if pattern not in all_treatments:
                raise ValueError(f"Treatment not found: {pattern}. Available: {treatment_names}")
            expanded.append(pattern)

    return list(dict.fromkeys(expanded))  # Deduplicate while preserving order


def generate_test_params(task_filter: str | None, treatment_filter: str | None):
    """Generate (task_name, treatment_name) pairs based on filters.

    - No filters: returns default_treatments for each task (from task.toml)
    - --task only: returns default_treatments for that task
    - --treatment only: returns that treatment for all tasks (comma-separated and wildcards supported)
    - Both: returns those specific combinations
    """
    params = []
    all_treatments = load_treatments()
    all_tasks = list_tasks()

    # Validate task filter
    if task_filter and task_filter not in all_tasks:
        raise ValueError(f"Task not found: {task_filter}. Available: {all_tasks}")

    # Parse and expand treatment filter (supports comma-separated and wildcards)
    treatment_list = []
    if treatment_filter:
        patterns = [t.strip() for t in treatment_filter.split(",")]
        treatment_list = expand_treatment_patterns(patterns, all_treatments)

    # Determine which tasks to run
    tasks_to_run = [task_filter] if task_filter else all_tasks

    for task_name in tasks_to_run:
        task = load_task(task_name)
        if treatment_list:
            # Specific treatments requested - use them
            for treatment_name in treatment_list:
                params.append((task_name, treatment_name))
        else:
            # No treatment filter - use defaults from task.toml
            for treatment_name in task.default_treatments:
                if treatment_name in all_treatments:
                    params.append((task_name, treatment_name))

    return params


def pytest_generate_tests(metafunc):
    """Dynamically parametrize tests based on CLI options."""
    if "task_name" in metafunc.fixturenames and "treatment_name" in metafunc.fixturenames:
        task_filter = metafunc.config.getoption("--task")
        treatment_filter = metafunc.config.getoption("--treatment")
        params = generate_test_params(task_filter, treatment_filter)
        metafunc.parametrize("task_name,treatment_name", params)


def run_validators(validators: list, test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run function-based validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in validators:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed


@pytest.mark.langsmith(
    test_suite_name=os.environ.get("LANGSMITH_TEST_SUITE", "skills-benchmark"),
    inputs={},  # Disable auto-capture, use ls_testing.log_inputs() instead
)
@pytest.mark.timeout(PYTEST_TIMEOUT)
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
    upload_traces,
):
    """Run a task with a treatment and validate results."""
    # Load task
    task = load_task(task_name)

    # Load all shared treatments
    treatments = load_treatments()
    if treatment_name not in treatments:
        pytest.skip(f"Treatment {treatment_name} not found")
    treatment_cfg = treatments[treatment_name]

    # Load validators from task
    validators = task.load_validators()

    # Build treatment
    skills = build_treatment_skills(treatment_cfg.skills) if treatment_cfg.skills else {}
    noise_tasks = build_noise_tasks(treatment_cfg.noise_tasks) if treatment_cfg.noise_tasks else []

    treatment = Treatment(
        description=treatment_cfg.description,
        skills=skills,
        claude_md=treatment_cfg.claude_md if treatment_cfg.claude_md else None,
        noise_tasks=noise_tasks,
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

    # Upload fixture traces for tasks that need them (ls-multiskill-*)
    trace_id_map = {}
    if task_name.startswith("ls-multiskill"):
        data_dir = task.path / "data"
        if data_dir.exists():
            trace_id_map = upload_traces(data_dir)

    # Render prompt with required variables
    template_vars = {"run_id": run_id}

    # Add task-specific variables (e.g., datasets for ls-lang-evaluator)
    if task_name == "ls-lang-evaluator":
        # These would come from fixtures in a real test
        template_vars["py_dataset"] = f"benchmark-sql-{run_id[:8]}"
        template_vars["ts_dataset"] = f"benchmark-support-{run_id[:8]}"

    prompt = task.render_prompt(**template_vars)
    prompt = treatment.build_prompt(prompt)

    # Log inputs to LangSmith
    ls_testing.log_inputs(
        {
            "task_name": task_name,
            "task_description": task.config.description,
            "environment_description": task.config.environment_description,
            "treatment_name": treatment_name,
            "treatment_description": treatment_cfg.description,
            "prompt": prompt,
            "skills_loaded": list(treatment.skills.keys()) if treatment.skills else [],
        }
    )

    # Run Claude
    result = run_claude(prompt, timeout=CLAUDE_TIMEOUT)

    # Parse output
    events = extract_events(parse_output(result.stdout))

    # Run validators
    outputs = {
        "run_id": run_id,
        "langsmith_project": langsmith_project,
        "treatment_name": treatment_name,
        "events": events,
        "noise_tasks": treatment_cfg.noise_tasks,
        "trace_id_map": trace_id_map,
    }
    passed, failed = run_validators(validators, test_dir, outputs)

    # Log outputs to LangSmith
    ls_testing.log_outputs(
        {
            "skills_invoked": events.get("skills_invoked", []),
            "files_produced": events.get("files_created", []),
            "passed_checks": passed,
            "failed_checks": failed,
        }
    )

    # Log feedback scores to LangSmith
    total_checks = len(passed) + len(failed)
    duration = events.get("duration_seconds", 0)
    num_turns = events.get("num_turns", 0)

    # Duration in seconds
    if duration:
        ls_testing.log_feedback(key="duration_seconds", score=float(duration))

    # Number of turns
    if num_turns:
        ls_testing.log_feedback(key="num_turns", score=float(num_turns))

    # Checks pass rate (percentage of validation checks passed)
    if total_checks > 0:
        checks_pass_rate = len(passed) / total_checks
        ls_testing.log_feedback(key="checks_pass_rate", score=checks_pass_rate)

    # Record results
    record_result(events, passed, failed, run_id=run_id)

    assert not failed, f"Validation failed: {failed}"
