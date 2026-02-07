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
    bool_column, run_parallel, create_work_items,
    build_docker_image, run_in_docker,
)
from tests.langsmith_synergy.config import (
    TREATMENTS, build_prompt,
    BASIC_COMPARISON, ADVANCED_COMPARISON, ALL_TREATMENTS_LIST,
)
from tests.langsmith_synergy.validation.ground_truth import generate_all_ground_truth

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
VALIDATION_DIR = Path(__file__).parent / "validation"
REQUIRED_FILES = ["Dockerfile", "requirements.txt"]

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
    Builds Docker image from environment/, runs sql_agent.py from validation/.
    """
    if verbose:
        print("\n" + "=" * 60)
        print("PRE-GENERATING TRACES")
        print("=" * 60)
        print("Running sql_agent.py to generate traces in LangSmith...")

    # Build image from environment/ (has Dockerfile)
    image_name = build_docker_image(ENVIRONMENT_DIR, verbose=verbose)
    if not image_name:
        print("ERROR: Failed to build Docker image")
        return False

    # Run sql_agent.py from validation/ (has sql_agent.py + chinook.db)
    try:
        result = run_in_docker(
            VALIDATION_DIR,
            ["python", "sql_agent.py"],
            timeout=300,
            image_name=image_name,
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr

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

    except Exception as e:
        if verbose:
            print(f"ERROR: Failed to run sql_agent.py: {e}")
        return False


def generate_ground_truth(base_dir: Path, verbose: bool = True) -> None:
    """Generate ground truth ONCE for all treatments.

    Saves to base_dir/ground_truth/ - the runner automatically copies from there.

    This ensures all treatments are validated against the same expected data,
    avoiding race conditions from generating ground truth per-treatment.
    """
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

        # Show the distinct questions
        dataset = gt_data.get("dataset", {})
        examples = dataset.get("examples", [])
        print(f"\nExpected traces ({len(examples)}):")
        for ex in examples:
            inputs = ex.get("inputs", {})
            msgs = inputs.get("messages", [])
            question = msgs[0].get("content", "?")[:60] if msgs else "?"
            trajectory = ex.get("outputs", {}).get("expected_trajectory", [])
            print(f"  - {question}... ({len(trajectory)} tools)")

        print("=" * 60 + "\n")


def cleanup_langsmith_datasets(run_ids: List[str] = None, verbose: bool = True) -> int:
    """Delete LangSmith datasets created during the experiment.

    Args:
        run_ids: List of run_ids to delete (datasets named "test-{run_id}")
                 If None, no datasets are deleted (safe default)
        verbose: Print cleanup progress

    Returns:
        Number of datasets deleted
    """
    if not run_ids:
        if verbose:
            print("No run_ids provided for cleanup, skipping")
        return 0

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

        # Find datasets matching our specific run_ids
        datasets = list(client.list_datasets())
        prefixes = [f"test-{rid}" for rid in run_ids]
        test_datasets = [d for d in datasets if any(d.name.startswith(p) for p in prefixes)]

        if not test_datasets:
            if verbose:
                print(f"No datasets found for {len(run_ids)} run_ids")
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
        print(f"\n{'Treatment':<20} {'Checks':<18} {'Skills':<10} {'Turns':<8} {'Duration':<10} {'Failures':<40}")
        print("-" * 120)

        for name, runs in results.items():
            # Calculate checks passed/total
            checks_passed = sum(len(r.checks_passed) for r in runs)
            checks_total = sum(len(r.checks_passed) + len(r.checks_failed) for r in runs)
            check_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
            checks_str = f"{checks_passed}/{checks_total} ({check_pct:.0f}%)"

            # Count skill invocations (not "Note: did not invoke")
            skill_count = sum(1 for r in runs if any(
                ('Invoked' in c and 'langsmith' in c.lower())
                for c in r.checks_passed
            ))
            skill_rate = f"{skill_count}/{len(runs)}"

            turns = [r.events.get("num_turns") for r in runs if r.events and r.events.get("num_turns")]
            durations = [r.events.get("duration_seconds") for r in runs if r.events and r.events.get("duration_seconds")]
            avg_turns = f"{sum(turns)/len(turns):.0f}" if turns else "N/A"
            avg_dur = f"{sum(durations)/len(durations):.0f}s" if durations else "N/A"

            # Show first failure reason
            failures = [f for r in runs for f in r.checks_failed[:1]]
            failure_msg = failures[0][:38] if failures else "-"

            print(f"{name:<20} {checks_str:<18} {skill_rate:<10} {avg_turns:<8} {avg_dur:<10} {failure_msg:<40}")
    else:
        print(f"\n{'Treatment':<20} {'Checks':<15} {'Turns':<8} {'Duration':<10} {'Details'}")
        print("-" * 120)

        for name, runs in results.items():
            r = runs[0]
            checks_passed = len(r.checks_passed)
            checks_total = checks_passed + len(r.checks_failed)
            check_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
            checks_str = f"{checks_passed}/{checks_total} ({check_pct:.0f}%)"
            turns = str(r.events.get("num_turns", "?")) if r.events else "?"
            dur = r.events.get('duration_seconds') if r.events else None
            duration = f"{dur:.0f}s" if dur else "?"
            details = f"Failed: {r.checks_failed[0][:35]}" if r.checks_failed else ", ".join(c[:25] for c in r.checks_passed[:3])
            print(f"{name:<20} {checks_str:<15} {turns:<8} {duration:<10} {details}")

    print("-" * 120)
    total_checks_passed = sum(sum(len(r.checks_passed) for r in runs) for runs in results.values())
    total_checks = sum(sum(len(r.checks_passed) + len(r.checks_failed) for r in runs) for runs in results.values())
    total_pct = (total_checks_passed / total_checks * 100) if total_checks > 0 else 0
    print(f"\nSummary: {total_checks_passed}/{total_checks} checks passed ({total_pct:.1f}%)")
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
                        "Whether the evaluator passed tests (checks for 'X/4 tests' in results)"),
        ],
    )

    # Generate seed traces
    if not args.skip_traces:
        if not generate_traces():
            print("WARNING: Trace generation had errors. Continuing anyway...")
        # Wait for LangSmith to fully index tool runs (eventual consistency)
        print("Waiting 10s for LangSmith to index traces...")
        time.sleep(10)

    # Generate ground truth ONCE before any treatments run
    # Saved to base_dir/ground_truth/ - runner automatically copies from there
    generate_ground_truth(experiment.base_dir)

    print(f"LANGSMITH SYNERGY EXPERIMENT\n{'='*60}")
    print(f"Experiment: {experiment.experiment_id}")
    print(f"Treatments: {', '.join(treatments)}")
    print(f"Repetitions: {args.repeat}, Workers: {args.workers}\n")

    work_items = create_work_items(
        treatments=TREATMENTS,
        treatment_names=treatments,
        base_dir=experiment.base_dir,
        build_prompt_func=build_prompt,
        environment_dir=ENVIRONMENT_DIR,
        repeat=args.repeat,
        timeout=args.timeout,
        model=args.model,
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
                run_id=r.run_id,
            ))

    print_report(all_results)
    experiment.finalize()

    # Cleanup LangSmith datasets after all treatments complete
    if not args.skip_cleanup:
        run_ids = [w.run_id for w in work_items if w.run_id]
        cleanup_langsmith_datasets(run_ids=run_ids, verbose=True)

    total = sum(len(runs) for runs in all_results.values())
    passed = sum(sum(1 for r in runs if r.passed) for runs in all_results.values())
    return 0 if passed > total // 2 else 1


if __name__ == "__main__":
    sys.exit(main())
