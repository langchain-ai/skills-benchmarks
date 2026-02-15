"""Shared runner for LangSmith Synergy tests.

Used by test_basic.py and test_advanced.py to run treatments.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    TestResult, verify_environment,
    ExperimentLogger, TreatmentResult,
    bool_column, run_parallel, create_work_items,
    build_docker_image, run_in_docker,
    Treatment,
)
from tests.langsmith_synergy.validation.ground_truth import generate_all_ground_truth

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
VALIDATION_DIR = Path(__file__).parent / "validation"
REQUIRED_FILES = ["Dockerfile", "requirements.txt"]


def generate_traces(verbose: bool = True) -> bool:
    """Run sql_agent.py to generate traces in LangSmith."""
    if verbose:
        print("\n" + "=" * 60)
        print("PRE-GENERATING TRACES")
        print("=" * 60)

    image_name = build_docker_image(ENVIRONMENT_DIR, verbose=verbose)
    if not image_name:
        print("ERROR: Failed to build Docker image")
        return False

    try:
        result = run_in_docker(
            VALIDATION_DIR,
            ["python", "sql_agent.py"],
            timeout=300,
            image_name=image_name,
        )
        success = result.returncode == 0
        if verbose:
            if success:
                print("SUCCESS: Traces generated")
            else:
                print("WARNING: sql_agent.py returned errors")
            print("=" * 60 + "\n")
        time.sleep(2)
        return success
    except Exception as e:
        if verbose:
            print(f"ERROR: Failed to run sql_agent.py: {e}")
        return False


def generate_ground_truth(base_dir: Path, verbose: bool = True) -> None:
    """Generate ground truth ONCE for all treatments."""
    if verbose:
        print("\n" + "=" * 60)
        print("GENERATING GROUND TRUTH")
        print("=" * 60)

    gt_dir = base_dir / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)
    gt_data = generate_all_ground_truth(gt_dir)

    if verbose:
        trace_count = gt_data.get("trace_count", 0)
        example_count = gt_data.get("dataset_example_count", 0)
        print(f"Generated: {trace_count} traces, {example_count} examples")
        print("=" * 60 + "\n")


def cleanup_langsmith_datasets(run_ids: List[str] = None, verbose: bool = True) -> int:
    """Delete LangSmith datasets created during the experiment."""
    if not run_ids:
        return 0

    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return 0

    try:
        from langsmith import Client
        client = Client(api_key=api_key)
        datasets = list(client.list_datasets())
        prefixes = [f"test-{rid}" for rid in run_ids]
        test_datasets = [d for d in datasets if any(d.name.startswith(p) for p in prefixes)]

        deleted = 0
        for dataset in test_datasets:
            try:
                client.delete_dataset(dataset_id=dataset.id)
                deleted += 1
            except Exception:
                pass
        return deleted
    except Exception:
        return 0


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
    skip_traces: bool = False,
    skip_cleanup: bool = False,
) -> Dict[str, List[TestResult]]:
    """Run an experiment with the given treatments.

    Args:
        treatments: Dict of treatment_name -> Treatment
        build_prompt_func: Function to build prompts
        validate_func: Function to validate results (must be module-level for pickling)
        experiment_name: Name for the experiment
        ...

    Returns dict of treatment_name -> list of TestResult.
    """
    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)

    if treatment_names is None:
        treatment_names = list(treatments.keys())

    experiment = ExperimentLogger(
        experiment_name,
        columns=[
            bool_column("Trace Skill", "Invoked langsmith-trace skill",
                        "Whether Claude invoked the langsmith-trace skill"),
            bool_column("Dataset Skill", "Invoked langsmith-dataset skill",
                        "Whether Claude invoked the langsmith-dataset skill"),
            bool_column("Evaluator Skill", "Invoked langsmith-evaluator skill",
                        "Whether Claude invoked the langsmith-evaluator skill"),
            bool_column("Trace Tests", "Traces:",
                        "Whether traces are available in LangSmith project"),
            bool_column("Dataset Tests", "have trajectory",
                        "Whether dataset has valid trajectory structure"),
            bool_column("Eval Tests", "/4 tests",
                        "Whether the evaluator passed tests"),
        ],
    )

    # Generate seed traces
    if not skip_traces:
        if not generate_traces():
            print("WARNING: Trace generation had errors. Continuing anyway...")
        print("Waiting 10s for LangSmith to index traces...")
        time.sleep(10)

    # Generate ground truth
    generate_ground_truth(experiment.base_dir)

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

    # Cleanup
    if not skip_cleanup:
        run_ids = [w.run_id for w in work_items if w.run_id]
        cleanup_langsmith_datasets(run_ids=run_ids)

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


