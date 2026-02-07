#!/usr/bin/env python3
"""LangSmith Synergy experiment runner (parallel execution).

Tests whether Claude can use multiple LangSmith skills together effectively.

Usage:
    python tests/langsmith_synergy/test_langsmith_synergy.py -t basic -r 3
    python tests/langsmith_synergy/test_langsmith_synergy.py -t advanced -r 3
    python tests/langsmith_synergy/test_langsmith_synergy.py -t all -r 3 -w 4
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    TestResult, verify_environment,
    ExperimentLogger, TreatmentResult,
    bool_column, quality_column,
    run_parallel, create_work_items,
    run_python_in_docker, build_docker_image,
)
from tests.langsmith_synergy.config import (
    TREATMENTS, build_prompt,
    BASIC_COMPARISON, ADVANCED_COMPARISON, ALL_TREATMENTS_LIST,
)

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt", "chinook.db", "sql_agent.py"]

PRESETS = {
    "basic": BASIC_COMPARISON,
    "advanced": ADVANCED_COMPARISON,
    "all": ALL_TREATMENTS_LIST,
}


def expand_treatments(args: list[str]) -> list[str]:
    """Expand preset names to treatment lists."""
    result = []
    for arg in args:
        if arg in PRESETS:
            result.extend(PRESETS[arg])
        elif arg in TREATMENTS:
            result.append(arg)
        else:
            print(f"Unknown: {arg}")
            print(f"Treatments: {', '.join(TREATMENTS.keys())}")
            print(f"Presets: {', '.join(PRESETS.keys())}")
            sys.exit(1)
    return result


def generate_traces(verbose: bool = True) -> bool:
    """Run sql_agent.py to generate traces in LangSmith.

    This must be done before the synergy tests so Claude has traces to work with.
    """
    if verbose:
        print("\n" + "=" * 60)
        print("PRE-GENERATING TRACES")
        print("=" * 60)
        print("Running sql_agent.py to generate traces in LangSmith...")

    image_name = build_docker_image(ENVIRONMENT_DIR, verbose=verbose)
    if not image_name:
        print("ERROR: Failed to build Docker image")
        return False

    success, output = run_python_in_docker(ENVIRONMENT_DIR, "sql_agent.py", timeout=300)

    if verbose:
        if success:
            print("SUCCESS: Traces generated")
            for line in output.strip().split('\n')[-5:]:
                print(f"  {line}")
        else:
            print(f"WARNING: sql_agent.py returned errors (traces may still exist)")
            print(output[:500] if len(output) > 500 else output)
        print("=" * 60 + "\n")

    time.sleep(2)  # Give LangSmith time to index
    return success


def cleanup_langsmith_datasets(prefix: str = "test-", verbose: bool = True) -> int:
    """Delete LangSmith datasets created during the experiment.

    Args:
        prefix: Dataset name prefix to match (default: "test-")
        verbose: Print cleanup progress

    Returns:
        Number of datasets deleted
    """
    if verbose:
        print("\n" + "=" * 60)
        print("CLEANING UP LANGSMITH DATASETS")
        print("=" * 60)

    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        if verbose:
            print("LANGSMITH_API_KEY not set, skipping cleanup")
        return 0

    try:
        from langsmith import Client
        client = Client(api_key=api_key)

        # Find datasets matching our test prefix
        datasets = list(client.list_datasets())
        test_datasets = [d for d in datasets if d.name.startswith(prefix)]

        if not test_datasets:
            if verbose:
                print(f"No datasets found with prefix '{prefix}'")
            return 0

        if verbose:
            print(f"Found {len(test_datasets)} test datasets to delete:")
            for d in test_datasets:
                print(f"  - {d.name}")

        deleted = 0
        for dataset in test_datasets:
            try:
                client.delete_dataset(dataset_id=dataset.id)
                deleted += 1
                if verbose:
                    print(f"  Deleted: {dataset.name}")
            except Exception as e:
                if verbose:
                    print(f"  Failed to delete {dataset.name}: {e}")

        if verbose:
            print(f"Cleaned up {deleted}/{len(test_datasets)} datasets")
            print("=" * 60 + "\n")

        return deleted

    except ImportError:
        if verbose:
            print("langsmith not installed, skipping cleanup")
        return 0
    except Exception as e:
        if verbose:
            print(f"Cleanup error: {e}")
        return 0


def validate_treatment(events: dict, test_dir: Path, treatment_name: str, outputs: dict):
    """Validate using the treatment's validators."""
    from tests.langsmith_synergy.config import TREATMENTS

    treatment = TREATMENTS.get(treatment_name)
    if treatment:
        return treatment.validate(events, test_dir, outputs)
    return [], [f"Unknown treatment: {treatment_name}"]


def print_report(results: Dict[str, List[TestResult]]):
    """Print experiment results summary."""
    print("\n" + "=" * 120)
    print("  LANGSMITH SYNERGY EXPERIMENT RESULTS")
    print("=" * 120)

    has_reps = any(len(runs) > 1 for runs in results.values())

    if has_reps:
        print(f"\n{'Treatment':<20} {'Pass':<10} {'Trace':<10} {'Dataset':<10} {'Eval':<10} {'Turns':<8} {'Duration':<10}")
        print("-" * 120)

        for name, runs in results.items():
            n = len(runs)
            pass_rate = f"{sum(1 for r in runs if r.passed)}/{n}"
            trace_rate = f"{sum(1 for r in runs if any('langsmith-trace' in c for c in r.checks_passed))}/{n}"
            dataset_rate = f"{sum(1 for r in runs if any('langsmith-dataset' in c for c in r.checks_passed))}/{n}"
            eval_rate = f"{sum(1 for r in runs if any('langsmith-evaluator' in c for c in r.checks_passed))}/{n}"

            turns = [r.events.get("num_turns") for r in runs if r.events and r.events.get("num_turns")]
            durations = [r.events.get("duration_seconds") for r in runs if r.events and r.events.get("duration_seconds")]
            avg_turns = f"{sum(turns)/len(turns):.0f}" if turns else "N/A"
            avg_dur = f"{sum(durations)/len(durations):.0f}s" if durations else "N/A"

            print(f"{name:<20} {pass_rate:<10} {trace_rate:<10} {dataset_rate:<10} {eval_rate:<10} {avg_turns:<8} {avg_dur:<10}")
    else:
        print(f"\n{'Treatment':<20} {'Result':<8} {'Turns':<8} {'Duration':<10} {'Key Checks'}")
        print("-" * 120)

        for name, runs in results.items():
            r = runs[0]
            status = "PASS" if r.passed else "FAIL"
            turns = str(r.events.get("num_turns", "?")) if r.events else "?"
            dur = r.events.get('duration_seconds') if r.events else None
            duration = f"{dur:.0f}s" if dur else "?"
            checks = f"FAIL: {r.checks_failed[0][:40]}" if r.checks_failed else ", ".join(c[:30] for c in r.checks_passed[:3])
            print(f"{name:<20} {status:<8} {turns:<8} {duration:<10} {checks}")

    print("-" * 120)
    total = sum(len(runs) for runs in results.values())
    passed = sum(sum(1 for r in runs if r.passed) for runs in results.values())
    print(f"\nSummary: {passed}/{total} runs passed")
    print("=" * 120)


def main():
    parser = argparse.ArgumentParser(description="LangSmith synergy experiment")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-t", "--treatments", nargs="+", metavar="NAME", help="Treatments or presets")
    parser.add_argument("-r", "--repeat", type=int, default=1, help="Repetitions per treatment")
    parser.add_argument("-w", "--workers", type=int, default=3, help="Parallel workers")
    parser.add_argument("-n", "--name", type=str, help="Experiment name")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per run (seconds)")
    parser.add_argument("--skip-traces", action="store_true", help="Skip trace generation")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip LangSmith dataset cleanup")
    args = parser.parse_args()

    if not args.treatments:
        print("Use -t to specify treatments or presets")
        print(f"Presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)
    treatments = expand_treatments(args.treatments)

    experiment = ExperimentLogger(
        args.name or "_".join(treatments[:3]),
        columns=[
            bool_column("Trace Skill", "Invoked langsmith-trace"),
            bool_column("Dataset Skill", "Invoked langsmith-dataset"),
            bool_column("Evaluator Skill", "Invoked langsmith-evaluator"),
            quality_column("Quality"),
        ],
    )

    # Generate seed traces
    if not args.skip_traces:
        if not generate_traces():
            print("WARNING: Trace generation had errors. Continuing anyway...")

    print(f"LANGSMITH SYNERGY EXPERIMENT\n{'='*60}")
    print(f"Experiment: {experiment.experiment_id}")
    print(f"Treatments: {', '.join(treatments)}")
    print(f"Repetitions: {args.repeat}, Workers: {args.workers}\n")

    # Path to ground truth generators
    validation_module = str(Path(__file__).parent / "validation" / "ground_truth.py")

    work_items = create_work_items(
        treatments=TREATMENTS,
        treatment_names=treatments,
        base_dir=experiment.base_dir,
        build_prompt_func=build_prompt,
        environment_dir=ENVIRONMENT_DIR,
        repeat=args.repeat,
        timeout=args.timeout,
        model=args.model,
        validation_module=validation_module,
    )

    print(f"Total runs: {len(work_items)}\n")

    all_results = run_parallel(work_items, validate_treatment, max_workers=args.workers)

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
            ))

    print_report(all_results)
    experiment.finalize()

    # Cleanup LangSmith datasets after all treatments complete
    if not args.skip_cleanup:
        cleanup_langsmith_datasets(prefix="test-", verbose=True)

    total = sum(len(runs) for runs in all_results.values())
    passed = sum(sum(1 for r in runs if r.passed) for runs in all_results.values())
    return 0 if passed > total // 2 else 1


if __name__ == "__main__":
    sys.exit(main())
