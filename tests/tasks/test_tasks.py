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
from conftest import register_run_id_for_cleanup
from langsmith import testing as ls_testing
from langsmith.run_helpers import get_current_run_tree
from langsmith.run_helpers import trace as ls_trace

from scaffold import NoiseTask, Treatment
from scaffold.python import extract_events, parse_output
from scaffold.python.external_data_handler import run_task_handlers
from scaffold.python.tasks import list_tasks, load_task
from scaffold.python.treatments import build_treatment_skills, load_treatments
from scaffold.python.validation import NOISE_TASK_DELIVERABLES, NOISE_TASK_PROMPTS

# Timeouts
CLAUDE_TIMEOUT = 600  # 10 minutes for Claude to complete task
PYTEST_TIMEOUT = 900  # 15 minutes total including setup/teardown


# =============================================================================
# PARAMETRIZE HELPERS
# =============================================================================


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


# =============================================================================
# TEST HELPERS
# =============================================================================


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


def set_experiment_trace_env() -> list[str]:
    """Set env vars so the stop hook nests CC traces under the experiment run.

    Returns list of env var keys that were set (for cleanup).
    """
    run_tree = get_current_run_tree()
    if not run_tree:
        return []

    os.environ["CC_LS_TRACE_ID"] = str(run_tree.trace_id)
    os.environ["CC_LS_PARENT_RUN_ID"] = str(run_tree.id)
    os.environ["CC_LS_DOTTED_ORDER"] = run_tree.dotted_order or ""
    if run_tree.session_name:
        os.environ["CC_LANGSMITH_PROJECT"] = run_tree.session_name
    return ["CC_LS_TRACE_ID", "CC_LS_PARENT_RUN_ID", "CC_LS_DOTTED_ORDER", "CC_LANGSMITH_PROJECT"]


def run_validators(validators: list, test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
    """Run function-based validators and return combined results."""
    all_passed, all_failed = [], []
    for validator in validators:
        with ls_trace(
            name=validator.__name__,
            inputs={
                "treatment_name": outputs.get("treatment_name"),
                "run_id": outputs.get("run_id"),
            },
        ):
            passed, failed = validator(test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)
    return all_passed, all_failed


# =============================================================================
# TEST
# =============================================================================


@pytest.mark.langsmith(
    test_suite_name=os.environ.get("LANGSMITH_TEST_SUITE", "skills-benchmark"),
)
@pytest.mark.timeout(PYTEST_TIMEOUT)
def test_task_treatment(task_name, treatment_name, fixtures):
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
    )

    # Setup test context with task's environment
    fixtures.setup_test_context(
        skills=treatment.skills,
        claude_md=treatment.claude_md,
        environment_dir=task.environment_dir,
    )

    # Generate run_id for namespace isolation and cleanup
    run_id = str(uuid.uuid4())
    register_run_id_for_cleanup(run_id)

    # Execute data handlers from task config
    trace_id_map = run_task_handlers(
        task.config.setup.data_handlers,
        task.data_dir,
        fixtures.langsmith_env,
        run_id,
    )

    # Build template variables from config
    template_vars = {"run_id": run_id}
    for var_name, var_template in task.config.setup.template_vars.items():
        template_vars[var_name] = var_template.format(run_id=run_id)

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

    # Pass experiment trace context to Docker so stop_hook nests CC traces
    # under the experiment run (visible when clicking the experiment row)
    cc_env_keys = set_experiment_trace_env()

    # Run Claude
    try:
        result = fixtures.run_claude(prompt, timeout=CLAUDE_TIMEOUT)
    finally:
        for key in cc_env_keys:
            os.environ.pop(key, None)

    # Parse output
    events = extract_events(parse_output(result.stdout))

    # Run validators
    outputs = {
        "run_id": run_id,
        "langsmith_env": fixtures.langsmith_env,
        "treatment_name": treatment_name,
        "events": events,
        "noise_tasks": treatment_cfg.noise_tasks,
        "trace_id_map": trace_id_map,
    }
    # Wrap all validators — creates parent evaluator trace in "evaluators" project
    with ls_testing.trace_feedback(name="Validation"):
        passed, failed = run_validators(validators, fixtures.test_dir, outputs)

        # checks_pass_rate inside context → linked to evaluator trace
        total_checks = len(passed) + len(failed)
        if total_checks > 0:
            ls_testing.log_feedback(
                key="checks_pass_rate",
                score=len(passed) / total_checks,
            )

    # Update outputs with final results
    ls_testing.log_outputs(
        {
            "skills_invoked": events.get("skills_invoked", []),
            "passed_checks": passed,
            "failed_checks": failed,
        }
    )

    # Duration/turns stay outside (Claude metrics, not validator results)
    duration = events.get("duration_seconds", 0)
    num_turns = events.get("num_turns", 0)

    if duration:
        ls_testing.log_feedback(key="duration_seconds", score=float(duration))

    if num_turns:
        ls_testing.log_feedback(key="num_turns", score=float(num_turns))

    # Record results
    fixtures.record_result(events, passed, failed, run_id=run_id)

    # Use pytest.fail() instead of assert to get cleaner error messages
    # (assert shows the full expression evaluation which is noisy)
    if failed:
        pytest.fail(f"Validation failed: {failed}")
