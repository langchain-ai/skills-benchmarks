"""Generic test runner for task + treatment combinations.

This test file uses the task-based structure where:
- Tasks are self-contained directories with instruction.md, task.toml, environment/, validation/
- Treatments are shared across tasks in treatments/{category}/*.yaml
- Each task declares compatible_treatments in tasks/index.yaml

Usage:
    # Run all task/treatment combinations
    pytest tests/tasks/test_tasks.py -v

    # Run specific task
    pytest tests/tasks/test_tasks.py -k "ls-evaluator" -v

    # Run specific treatment
    pytest tests/tasks/test_tasks.py -k "LS_BASIC_PY" -v

    # Run specific combination
    pytest tests/tasks/test_tasks.py -k "ls-evaluator and LS_BASIC_BOTH" -v
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


def load_task_index() -> dict:
    """Load the task index with compatible treatments."""
    if not TASK_INDEX.exists():
        return {}
    with open(TASK_INDEX) as f:
        data = yaml.safe_load(f)
    return data.get("tasks", {})


def generate_test_params():
    """Generate (task_name, treatment_name) pairs from task index compatible_treatments."""
    params = []
    task_index = load_task_index()
    all_treatments = load_treatments()

    for task_name in list_tasks():
        # Get compatible treatments from task index
        task_info = task_index.get(task_name, {})
        compatible = task_info.get("compatible_treatments", [])

        # Filter to only treatments that actually exist
        for treatment_name in compatible:
            if treatment_name in all_treatments:
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
