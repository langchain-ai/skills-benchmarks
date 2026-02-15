"""Shared runner for LangChain Agent tests.

Used by test_guidance.py, test_claudemd.py, and test_noise.py.
"""

import sys
from pathlib import Path
from typing import Dict, List, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    TestResult, verify_environment,
    ExperimentLogger, TreatmentResult,
    bool_column, quality_column, run_parallel, create_work_items,
    Treatment,
)

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt", "chinook.db"]


def run_experiment(
    treatments: Dict[str, Treatment],
    build_prompt_func: Callable,
    validate_func: Callable,
    experiment_name: str,
    treatment_names: List[str] = None,
    repeat: int = 1,
    workers: int = 3,
    timeout: int = 600,
    model: str = None,
) -> Dict[str, List[TestResult]]:
    """Run an experiment with the given treatments.

    Args:
        treatments: Dict of treatment_name -> Treatment
        build_prompt_func: Function to build prompts
        validate_func: Function to validate results (must be module-level for pickling)
        experiment_name: Name for the experiment
        treatment_names: List of treatment names to run (None = all)
        repeat: Number of repetitions per treatment
        workers: Number of parallel workers
        timeout: Timeout per run in seconds
        model: Model to use (None = default)

    Returns dict of treatment_name -> list of TestResult.
    """
    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)

    if treatment_names is None:
        treatment_names = list(treatments.keys())

    experiment = ExperimentLogger(
        experiment_name,
        columns=[
            bool_column("Skill", "Invoked langchain-agents skill",
                        "Whether Claude invoked the langchain-agents skill"),
            bool_column("Patterns", "imports create_agent",
                        "Whether the generated code uses modern create_agent patterns"),
            quality_column("Quality"),
        ],
    )

    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {experiment.experiment_id}")
    print(f"Treatments: {', '.join(treatment_names)}")
    print(f"Repetitions: {repeat}, Workers: {workers}")
    print(f"{'='*60}\n")

    work_items = create_work_items(
        treatments=treatments,
        treatment_names=treatment_names,
        base_dir=experiment.base_dir,
        build_prompt_func=build_prompt_func,
        environment_dir=ENVIRONMENT_DIR,
        repeat=repeat,
        timeout=timeout,
        model=model,
    )

    print(f"Total runs: {len(work_items)}\n")

    all_results = run_parallel(work_items, validate_func, max_workers=workers)

    # Log results
    for name, runs in all_results.items():
        for r in runs:
            events = r.events or {}
            experiment.add_result(name, TreatmentResult(
                name=r.name, passed=r.passed,
                checks_passed=r.checks_passed, checks_failed=r.checks_failed,
                events_summary={
                    "num_turns": events.get("num_turns"),
                    "duration_seconds": events.get("duration_seconds"),
                    "tool_calls": len(events.get("tool_calls", [])),
                },
                run_id=r.run_id,
            ))

    # Print summary
    print_summary(all_results)
    experiment.finalize()

    return all_results


def print_summary(results: Dict[str, List[TestResult]]):
    """Print experiment results summary."""
    print("\n" + "=" * 100)
    print("  RESULTS")
    print("=" * 100)

    print(f"\n{'Treatment':<25} {'Checks':<15} {'Turns':<8} {'Duration':<10} {'Details'}")
    print("-" * 100)

    for name, runs in results.items():
        for r in runs:
            checks_passed = len(r.checks_passed)
            checks_total = checks_passed + len(r.checks_failed)
            check_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
            checks_str = f"{checks_passed}/{checks_total} ({check_pct:.0f}%)"
            turns = str(r.events.get("num_turns", "?")) if r.events else "?"
            dur = r.events.get('duration_seconds') if r.events else None
            duration = f"{dur:.0f}s" if dur else "?"
            details = r.checks_failed[0][:30] if r.checks_failed else "OK"
            print(f"{name:<25} {checks_str:<15} {turns:<8} {duration:<10} {details}")

    print("-" * 100)
    total_passed = sum(sum(len(r.checks_passed) for r in runs) for runs in results.values())
    total = sum(sum(len(r.checks_passed) + len(r.checks_failed) for r in runs) for runs in results.values())
    print(f"Total: {total_passed}/{total} checks passed ({total_passed/total*100:.1f}%)" if total else "No results")
    print("=" * 100)
