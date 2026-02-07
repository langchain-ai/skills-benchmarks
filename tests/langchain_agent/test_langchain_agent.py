#!/usr/bin/env python3
"""LangChain Agent experiment runner (parallel execution).

Usage:
    python tests/langchain_agent/test_langchain_agent.py -t BASELINE
    python tests/langchain_agent/test_langchain_agent.py -t claudemd -r 3
    python tests/langchain_agent/test_langchain_agent.py -t all -r 3 -w 4
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
)
from tests.langchain_agent.config import (
    TREATMENTS, build_sql_prompt,
    REINFORCEMENT_COMPARISON, CONTROL_COMPARISON, CLAUDE_MD_COMPARISON,
    NOISE_COMPARISON, ALL_TREATMENTS,
)

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt", "chinook.db"]

PRESETS = {
    "reinforcement": REINFORCEMENT_COMPARISON,
    "claudemd": CLAUDE_MD_COMPARISON,
    "noise": NOISE_COMPARISON,
    "control": CONTROL_COMPARISON,
    "all": ALL_TREATMENTS,
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


# Module-level validation function (picklable for multiprocessing)
def validate_treatment(events: dict, test_dir: Path, treatment_name: str = None, outputs: dict = None):
    """Validate using the treatment's validators.

    Args:
        events: Parsed events from Claude's execution
        test_dir: Directory containing test files
        treatment_name: Name of the treatment to validate
        outputs: Pre-captured outputs {filename: (success, output, duration_s)}
    """
    from tests.langchain_agent.config import TREATMENTS

    if treatment_name is None:
        treatment_name = "BASELINE"

    treatment = TREATMENTS.get(treatment_name)
    if treatment:
        return treatment.validate(events, test_dir, outputs)
    return [], [f"Unknown treatment: {treatment_name}"]


def print_report(results: Dict[str, List[TestResult]]):
    """Print experiment results summary."""
    print("\n")
    print("=" * 120)
    print("  LANGCHAIN AGENT EXPERIMENT RESULTS")
    print("=" * 120)

    has_reps = any(len(runs) > 1 for runs in results.values())

    if has_reps:
        print(f"\n{'Treatment':<25} {'Checks':<18} {'Skill':<8} {'Patterns':<10} {'Turns':<8} {'Duration':<10}")
        print("-" * 120)

        for name, runs in results.items():
            n = len(runs)

            # Checks passed/total
            checks_passed = sum(len(r.checks_passed) for r in runs)
            checks_total = sum(len(r.checks_passed) + len(r.checks_failed) for r in runs)
            check_pct = (checks_passed / checks_total * 100) if checks_total > 0 else 0
            checks_str = f"{checks_passed}/{checks_total} ({check_pct:.0f}%)"

            skill_count = sum(1 for r in runs
                              if any("Invoked langchain-agents skill" in c for c in r.checks_passed))
            skill_rate = f"{skill_count}/{n}"

            pattern_count = sum(1 for r in runs
                                if any("imports create_agent" in c for c in r.checks_passed))
            pattern_rate = f"{pattern_count}/{n}"

            # Get avg metrics from events
            turns_list = [r.events.get("num_turns") for r in runs if r.events and r.events.get("num_turns")]
            durations = [r.events.get("duration_seconds") for r in runs if r.events and r.events.get("duration_seconds")]

            avg_turns = f"{sum(turns_list)/len(turns_list):.0f}" if turns_list else "N/A"
            avg_duration = f"{sum(durations)/len(durations):.0f}s" if durations else "N/A"

            print(f"{name:<25} {checks_str:<18} {skill_rate:<8} {pattern_rate:<10} {avg_turns:<8} {avg_duration:<10}")
    else:
        print(f"\n{'Treatment':<25} {'Checks':<18} {'Turns':<8} {'Duration':<10} {'Key Checks'}")
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

            if r.checks_failed:
                details_str = f"FAIL: {r.checks_failed[0][:40]}"
            else:
                key_checks = r.checks_passed[:3]
                details_str = ", ".join(c[:30] for c in key_checks)

            print(f"{name:<25} {checks_str:<18} {turns:<8} {duration:<10} {details_str}")

    print("-" * 120)

    # Summary with checks
    total_checks_passed = sum(sum(len(r.checks_passed) for r in runs) for runs in results.values())
    total_checks = sum(sum(len(r.checks_passed) + len(r.checks_failed) for r in runs) for runs in results.values())
    check_pct = (total_checks_passed / total_checks * 100) if total_checks > 0 else 0
    print(f"\nSummary: {total_checks_passed}/{total_checks} checks passed ({check_pct:.1f}%)")
    print("=" * 120)


def main():
    parser = argparse.ArgumentParser(description="LangChain agent experiment (parallel)")
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
    args = parser.parse_args()

    if not args.treatments:
        print("Use -t to specify treatments or presets")
        print(f"Presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    # Verify environment
    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)

    treatments = expand_treatments(args.treatments)

    # Create experiment logger
    experiment_name = args.name or "_".join(treatments[:3])
    experiment = ExperimentLogger(
        experiment_name,
        columns=[
            bool_column("Skill", "Invoked langchain-agents skill",
                        "Whether Claude invoked the langchain-agents skill"),
            bool_column("Patterns", "imports create_agent",
                        "Whether the generated code uses modern `create_agent` patterns"),
            quality_column("Quality"),
        ],
    )

    print(f"LANGCHAIN AGENT EXPERIMENT (PARALLEL)\n{'='*60}")
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
        build_prompt_func=build_sql_prompt,
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
