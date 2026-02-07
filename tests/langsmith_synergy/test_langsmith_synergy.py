#!/usr/bin/env python3
"""LangSmith Synergy experiment runner (parallel execution).

Tests whether Claude can use multiple LangSmith skills together effectively.

Usage:
    python tests/langsmith_synergy/test_langsmith_synergy.py -t basic -r 3
    python tests/langsmith_synergy/test_langsmith_synergy.py -t advanced -r 3
    python tests/langsmith_synergy/test_langsmith_synergy.py -t all -r 3 -w 4
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    TestResult, verify_environment,
    ExperimentLogger, TreatmentResult,
    bool_column, quality_column,
    WorkItem, run_parallel, create_work_items,
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

    Returns:
        True if traces were generated successfully
    """
    if verbose:
        print("\n" + "=" * 60)
        print("PRE-GENERATING TRACES")
        print("=" * 60)
        print("Running sql_agent.py to generate traces in LangSmith...")

    # Build the docker image first
    image_name = build_docker_image(ENVIRONMENT_DIR, verbose=verbose)
    if not image_name:
        print("ERROR: Failed to build Docker image")
        return False

    success, output = run_python_in_docker(ENVIRONMENT_DIR, "sql_agent.py", timeout=180)

    if verbose:
        if success:
            print("SUCCESS: Traces generated")
            # Show last few lines of output
            lines = output.strip().split('\n')
            for line in lines[-5:]:
                print(f"  {line}")
        else:
            print(f"WARNING: sql_agent.py returned errors (traces may still exist)")
            print(output[:500] if len(output) > 500 else output)
        print("=" * 60 + "\n")

    return success


# Module-level validation function (picklable for multiprocessing)
def validate_treatment(events: dict, test_dir: Path, treatment_name: str = None, outputs: dict = None):
    """Validate using the treatment's validators.

    Args:
        events: Parsed events from Claude's execution
        test_dir: Directory containing test files
        treatment_name: Name of the treatment to validate
        outputs: Pre-captured outputs {filename: (success, output, duration_s)}
    """
    from tests.langsmith_synergy.config import TREATMENTS

    if treatment_name is None:
        treatment_name = "BASIC_BASELINE"

    treatment = TREATMENTS.get(treatment_name)
    if treatment:
        return treatment.validate(events, test_dir, outputs)
    return [], [f"Unknown treatment: {treatment_name}"]


def print_report(results: Dict[str, List[TestResult]]):
    """Print experiment results summary."""
    print("\n")
    print("=" * 120)
    print("  LANGSMITH SYNERGY EXPERIMENT RESULTS")
    print("=" * 120)

    has_reps = any(len(runs) > 1 for runs in results.values())

    if has_reps:
        print(f"\n{'Treatment':<20} {'Pass':<10} {'Trace':<10} {'Dataset':<10} {'Eval':<10} {'Turns':<8} {'Duration':<10}")
        print("-" * 120)

        for name, runs in results.items():
            n = len(runs)
            pass_count = sum(1 for r in runs if r.passed)
            pass_rate = f"{pass_count}/{n}"

            trace_count = sum(1 for r in runs
                              if any("Invoked langsmith-trace" in c for c in r.checks_passed))
            trace_rate = f"{trace_count}/{n}"

            dataset_count = sum(1 for r in runs
                                if any("Invoked langsmith-dataset" in c for c in r.checks_passed))
            dataset_rate = f"{dataset_count}/{n}"

            eval_count = sum(1 for r in runs
                             if any("Invoked langsmith-evaluator" in c for c in r.checks_passed))
            eval_rate = f"{eval_count}/{n}"

            # Get avg metrics from events
            turns_list = [r.events.get("num_turns") for r in runs if r.events and r.events.get("num_turns")]
            durations = [r.events.get("duration_seconds") for r in runs if r.events and r.events.get("duration_seconds")]

            avg_turns = f"{sum(turns_list)/len(turns_list):.0f}" if turns_list else "N/A"
            avg_duration = f"{sum(durations)/len(durations):.0f}s" if durations else "N/A"

            print(f"{name:<20} {pass_rate:<10} {trace_rate:<10} {dataset_rate:<10} {eval_rate:<10} {avg_turns:<8} {avg_duration:<10}")
    else:
        print(f"\n{'Treatment':<20} {'Result':<8} {'Turns':<8} {'Duration':<10} {'Key Checks'}")
        print("-" * 120)

        for name, runs in results.items():
            r = runs[0]
            status = "PASS" if r.passed else "FAIL"
            turns = str(r.events.get("num_turns", "?")) if r.events else "?"
            dur = r.events.get('duration_seconds') if r.events else None
            duration = f"{dur:.0f}s" if dur else "?"

            if r.checks_failed:
                checks_str = f"FAIL: {r.checks_failed[0][:40]}"
            else:
                key_checks = r.checks_passed[:3]
                checks_str = ", ".join(c[:30] for c in key_checks)

            print(f"{name:<20} {status:<8} {turns:<8} {duration:<10} {checks_str}")

    print("-" * 120)

    total_runs = sum(len(runs) for runs in results.values())
    total_passed = sum(sum(1 for r in runs if r.passed) for runs in results.values())
    print(f"\nSummary: {total_passed}/{total_runs} runs passed")
    print("=" * 120)


def main():
    parser = argparse.ArgumentParser(description="LangSmith synergy experiment (parallel)")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-t", "--treatments", nargs="+", metavar="NAME",
                        help="Treatments or presets to run")
    parser.add_argument("-r", "--repeat", type=int, default=1,
                        help="Number of repetitions per treatment")
    parser.add_argument("-w", "--workers", type=int, default=3,
                        help="Number of parallel workers (default: 3)")
    parser.add_argument("-n", "--name", type=str,
                        help="Experiment name (for log folder)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Timeout per run in seconds (default: 600)")
    parser.add_argument("--skip-traces", action="store_true",
                        help="Skip trace generation (use existing traces)")
    args = parser.parse_args()

    if not args.treatments:
        print("Use -t to specify treatments or presets")
        print(f"Presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    # Verify environment
    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)

    treatments = expand_treatments(args.treatments)

    # Generate traces first (unless skipped)
    if not args.skip_traces:
        success = generate_traces()
        if not success:
            print("WARNING: Trace generation had errors. Continuing anyway...")

    # Create experiment logger
    experiment_name = args.name or "_".join(treatments[:3])
    experiment = ExperimentLogger(
        experiment_name,
        columns=[
            bool_column("Trace Skill", "Invoked langsmith-trace"),
            bool_column("Dataset Skill", "Invoked langsmith-dataset"),
            bool_column("Evaluator Skill", "Invoked langsmith-evaluator"),
            quality_column("Quality"),
        ],
    )

    print(f"LANGSMITH SYNERGY EXPERIMENT (PARALLEL)\n{'='*60}")
    print(f"Experiment: {experiment.experiment_id}")
    print(f"Treatments: {', '.join(treatments)}")
    print(f"Repetitions: {args.repeat}")
    print(f"Workers: {args.workers}")
    print()

    # Create work items
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

    print(f"Total runs: {len(work_items)}")
    print()

    # Run all treatments in parallel using module-level validator
    all_results = run_parallel(work_items, validate_treatment, max_workers=args.workers)

    # Add to experiment logger
    for name, runs in all_results.items():
        for r in runs:
            events = r.events or {}
            summary = {
                "num_turns": events.get("num_turns"),
                "duration_seconds": events.get("duration_seconds"),
                "tool_calls": len(events.get("tool_calls", [])),
            }
            treatment_result = TreatmentResult(
                name=r.name,
                passed=r.passed,
                checks_passed=r.checks_passed,
                checks_failed=r.checks_failed,
                events_summary=summary,
            )
            experiment.add_result(name, treatment_result)

    print_report(all_results)
    experiment.finalize()

    # Exit code based on pass rate
    total_passed = sum(sum(1 for r in runs if r.passed) for runs in all_results.values())
    total_runs = sum(len(runs) for runs in all_results.values())
    return 0 if total_passed > total_runs // 2 else 1


if __name__ == "__main__":
    sys.exit(main())
