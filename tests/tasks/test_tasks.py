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

    # Run specific task with all its default treatments
    pytest tests/tasks/test_tasks.py --task=ls-evaluator -v

    # Run specific treatment across all tasks that have it as default
    pytest tests/tasks/test_tasks.py --treatment=CONTROL -v
"""

import uuid
from pathlib import Path

import pytest
import yaml

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

# Tasks directory
TASKS_DIR = Path(__file__).parent.parent.parent / "tasks"
TASK_INDEX = TASKS_DIR / "index.yaml"


def pytest_addoption(parser):
    """Add CLI options for task and treatment selection."""
    parser.addoption(
        "--task",
        action="store",
        default=None,
        help="Run specific task (e.g., --task=ls-evaluator)",
    )
    parser.addoption(
        "--treatment",
        action="store",
        default=None,
        help="Run specific treatment (e.g., --treatment=LS_BASIC_PY)",
    )


def load_task_index() -> dict:
    """Load the task index with default treatments."""
    if not TASK_INDEX.exists():
        return {}
    with open(TASK_INDEX) as f:
        data = yaml.safe_load(f)
    return data.get("tasks", {})


def generate_test_params(task_filter: str | None, treatment_filter: str | None):
    """Generate (task_name, treatment_name) pairs based on filters.

    - No filters: returns default_treatments for each task
    - --task only: returns default_treatments for that task
    - --treatment only: returns that treatment for all tasks
    - Both: returns that specific combination
    """
    params = []
    task_index = load_task_index()
    all_treatments = load_treatments()
    all_tasks = list_tasks()

    # Validate filters
    if task_filter and task_filter not in all_tasks:
        raise ValueError(f"Task not found: {task_filter}. Available: {all_tasks}")
    if treatment_filter and treatment_filter not in all_treatments:
        raise ValueError(f"Treatment not found: {treatment_filter}. Available: {list(all_treatments.keys())}")

    # Determine which tasks to run
    tasks_to_run = [task_filter] if task_filter else all_tasks

    for task_name in tasks_to_run:
        if treatment_filter:
            # Specific treatment requested - use it
            params.append((task_name, treatment_filter))
        else:
            # No treatment filter - use defaults for this task
            task_info = task_index.get(task_name, {})
            defaults = task_info.get("default_treatments", [])
            for treatment_name in defaults:
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

    # Record results
    record_result(events, passed, failed, run_id=run_id)

    assert not failed, f"Validation failed: {failed}"
