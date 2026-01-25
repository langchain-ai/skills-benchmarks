#!/usr/bin/env python3
"""Test skill impact on LangChain pattern adherence.

Measures how guidance framing and location affect Claude's adherence to skill recommendations.

Usage:
    # Run all experiments
    .venv/bin/python tests/basic_skill/test_langchain_context.py

    # Run specific experiments
    .venv/bin/python tests/basic_skill/test_langchain_context.py -e SKILL_POS SKILL_NEG

    # Run a preset group (expands to multiple experiments)
    .venv/bin/python tests/basic_skill/test_langchain_context.py -e framing
    .venv/bin/python tests/basic_skill/test_langchain_context.py -e minimal-boost

    # Run with repetitions for statistical significance
    .venv/bin/python tests/basic_skill/test_langchain_context.py -e SKILL_POS -r 3
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold.setup import setup_test_environment, copy_test_data, cleanup_test_environment, setup_test_context
from scaffold.runner import run_test, run_with_repetition
from tests.basic_skill.experiments import (
    EXPERIMENTS, FRAMING_COMPARISON, LOCATION_COMPARISON,
    REITERATION_COMPARISON, POSITIVE_STRATEGY, NEGATIVE_STRATEGY,
    DIFFICULTY_COMPARISON, MINIMAL_BOOST_COMPARISON, NO_SQL_BOOST_COMPARISON,
    validate_sql_agent,
)

# Shared prompt for all experiments
PROMPT = """Build a LangChain SQL agent that can query chinook.db.
Requirements: Use gpt-4o-mini, only allow SELECT queries, include error handling.
Save to sql_agent.py and run a test query."""

CHINOOK_PATH = Path(__file__).parent / "chinook.db"

# Preset groups - shortcuts that expand to multiple experiments
PRESETS = {
    "framing": FRAMING_COMPARISON,
    "location": LOCATION_COMPARISON,
    "reiteration": REITERATION_COMPARISON,
    "positive": POSITIVE_STRATEGY,
    "negative": NEGATIVE_STRATEGY,
    "difficulty": DIFFICULTY_COMPARISON,
    "minimal-boost": MINIMAL_BOOST_COMPARISON,
    "nosql-boost": NO_SQL_BOOST_COMPARISON,
}


def make_test_dir(exp_name: str) -> Path:
    """Create test directory for an experiment."""
    desc, claude_md, sections = EXPERIMENTS[exp_name]
    test_dir = setup_test_environment()
    setup_test_context(test_dir, sections=sections, claude_md=claude_md)

    if CHINOOK_PATH.exists():
        copy_test_data(CHINOOK_PATH, test_dir)

    return test_dir


def expand_experiments(exp_args: list[str]) -> list[str]:
    """Expand preset names to actual experiment lists."""
    result = []
    for arg in exp_args:
        if arg in PRESETS:
            result.extend(PRESETS[arg])
        elif arg in EXPERIMENTS:
            result.append(arg)
        else:
            print(f"Unknown experiment or preset: {arg}")
            print(f"Available experiments: {', '.join(EXPERIMENTS.keys())}")
            print(f"Available presets: {', '.join(PRESETS.keys())}")
            sys.exit(1)
    return result


def run_experiments(experiments: list[str], repetitions: int, model: str = None) -> dict:
    """Run experiments and return results."""
    results = {}
    for exp_name in experiments:
        print(f"\n{'='*60}")
        print(f"{exp_name}: {EXPERIMENTS[exp_name][0]}")
        print('='*60)

        if repetitions > 1:
            results[exp_name] = run_with_repetition(
                exp_name, PROMPT, lambda en=exp_name: make_test_dir(en),
                validate_sql_agent, repetitions, model=model)
        else:
            test_dir = make_test_dir(exp_name)
            result = run_test(exp_name, PROMPT, test_dir, validate_sql_agent, model=model)
            cleanup_test_environment(test_dir)
            results[exp_name] = result

    return results


def print_report(results: dict, repetitions: int):
    """Print formatted report with side-by-side comparison."""
    print("\n")
    print("=" * 80)
    print("  RESULTS")
    print("=" * 80)

    # Extract efficiency metrics from checks
    def get_metrics(r):
        metrics = {"turns": None, "duration": None, "deprecated": 0}
        for check in r.checks_passed:
            if check.startswith("Turns:"):
                metrics["turns"] = int(check.split(":")[1].strip())
            elif check.startswith("Duration:"):
                metrics["duration"] = float(check.split(":")[1].strip().rstrip("s"))
            elif check.startswith("Deprecated attempts:"):
                metrics["deprecated"] = int(check.split(":")[1].strip())
        return metrics

    if repetitions > 1:
        # Repetition mode - show pass rates
        print(f"\n{'Experiment':<20} {'Pass Rate':<12} {'Consistent':<12}")
        print("-" * 50)
        for name in results.keys():
            r = results[name]
            rate = f"{r.pass_rate*100:.0f}%"
            consistent = "Yes" if r.consistent else "NO"
            print(f"{name:<20} {rate:<12} {consistent:<12}")
    else:
        # Single run mode - show detailed comparison
        print(f"\n{'Experiment':<20} {'Result':<8} {'Turns':<8} {'Time':<8} {'Deprecated':<12} {'Checks'}")
        print("-" * 80)
        for name in results.keys():
            r = results[name]
            metrics = get_metrics(r)
            result = "PASS" if r.passed else "FAIL"
            turns = str(metrics["turns"]) if metrics["turns"] else "-"
            duration = f"{metrics['duration']:.0f}s" if metrics["duration"] else "-"
            deprecated = str(metrics["deprecated"]) if metrics["deprecated"] else "0"
            # Filter out metrics from checks for display
            checks = [c for c in r.checks_passed[:3]
                     if not c.startswith(("Turns:", "Duration:", "Deprecated"))]
            checks_str = ", ".join(checks)
            if r.checks_failed:
                checks_str += f" | FAIL: {r.checks_failed[0]}"
            print(f"{name:<20} {result:<8} {turns:<8} {duration:<8} {deprecated:<12} {checks_str}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Test skill impact on LangChain pattern adherence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Presets (expand to multiple experiments):
  framing       - {', '.join(FRAMING_COMPARISON)}
  location      - {', '.join(LOCATION_COMPARISON)}
  difficulty    - {', '.join(DIFFICULTY_COMPARISON)}
  minimal-boost - {', '.join(MINIMAL_BOOST_COMPARISON)}
""")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-r", "--repetitions", type=int, default=1, help="Runs per experiment")
    parser.add_argument("-e", "--experiments", nargs="+", metavar="EXP",
                        help="Experiments or presets to run (default: all)")
    args = parser.parse_args()

    # Determine experiments to run
    if args.experiments:
        experiments_to_run = expand_experiments(args.experiments)
    else:
        experiments_to_run = list(EXPERIMENTS.keys())

    print("LANGCHAIN SKILL IMPACT TEST")
    print("=" * 60)
    print(f"Experiments: {', '.join(experiments_to_run)}")
    if args.repetitions > 1:
        print(f"Repetitions: {args.repetitions}")
    if args.model:
        print(f"Model: {args.model}")
    print()

    results = run_experiments(experiments_to_run, args.repetitions, args.model)
    print_report(results, args.repetitions)

    # Exit code based on results
    if args.repetitions > 1:
        return 0 if any(r.pass_rate > 0 for r in results.values()) else 1
    else:
        return 0 if any(r.passed for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
