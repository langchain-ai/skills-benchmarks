#!/usr/bin/env python3
"""Test context impact on LangChain skill following.

Measures how guidance framing and location affect Claude's adherence to skill recommendations.

Usage:
    # Run all cases once
    .venv/bin/python tests/context_impact/test_langchain_context.py

    # Run specific cases
    .venv/bin/python tests/context_impact/test_langchain_context.py -c SKILL_POS SKILL_NEG

    # Run with repetitions for statistical significance
    .venv/bin/python tests/context_impact/test_langchain_context.py -r 3

    # Run a comparison group
    .venv/bin/python tests/context_impact/test_langchain_context.py --compare framing
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold.setup import cleanup_test_environment
from scaffold.runner import run_test, run_with_repetition
from tests.context_impact.cases import (
    CASES, FRAMING_COMPARISON, LOCATION_COMPARISON,
    REITERATION_COMPARISON, POSITIVE_STRATEGY, NEGATIVE_STRATEGY,
)
from tests.context_impact.helpers import PROMPT, validate_sql_agent, make_test_dir

COMPARISON_GROUPS = {
    "framing": FRAMING_COMPARISON,
    "location": LOCATION_COMPARISON,
    "reiteration": REITERATION_COMPARISON,
    "positive": POSITIVE_STRATEGY,
    "negative": NEGATIVE_STRATEGY,
}


def run_cases(cases: list[str], repetitions: int, model: str = None) -> dict:
    """Run test cases and return results."""
    results = {}
    for case_name in cases:
        print(f"\n{'='*60}")
        print(f"{case_name}: {CASES[case_name][0]}")
        print('='*60)

        if repetitions > 1:
            results[case_name] = run_with_repetition(
                case_name, PROMPT, lambda cn=case_name: make_test_dir(cn),
                validate_sql_agent, repetitions, model=model)
        else:
            test_dir = make_test_dir(case_name)
            result = run_test(case_name, PROMPT, test_dir, validate_sql_agent, model=model)
            cleanup_test_environment(test_dir)
            results[case_name] = result

    return results


def print_report(results: dict, repetitions: int):
    """Print formatted report."""
    print("\n")
    print("=" * 70)
    print("  CONTEXT IMPACT ANALYSIS REPORT")
    print("=" * 70)

    # Results table
    print("\n--- RESULTS ---")
    print(f"{'Case':<15} {'Pass Rate':<12} {'Details'}")
    print("-" * 70)

    for name in sorted(results.keys()):
        r = results[name]
        if repetitions > 1:
            rate = f"{r.pass_rate*100:.0f}%"
            status = "consistent" if r.consistent else "INCONSISTENT"
            details = f"({status})"
        else:
            rate = "PASS" if r.passed else "FAIL"
            details = ", ".join(r.checks_passed[:3])
            if r.checks_failed:
                details += f" | FAILED: {', '.join(r.checks_failed)}"
        print(f"{name:<15} {rate:<12} {details}")

    # Comparison analysis (only if we have enough data)
    if repetitions > 1:
        _print_comparisons(results)

    print("\n" + "=" * 70)


def _print_comparisons(results: dict):
    """Print comparison analysis for repetition runs."""
    # Framing
    if all(n in results for n in FRAMING_COMPARISON):
        print("\n--- FRAMING: Negative vs Positive ---")
        neg, pos = results["SKILL_NEG"], results["SKILL_POS"]
        diff = pos.pass_rate - neg.pass_rate
        print(f"  SKILL_NEG: {neg.pass_rate*100:.0f}%  |  SKILL_POS: {pos.pass_rate*100:.0f}%  |  Diff: {diff*100:+.0f}%")

    # Location
    if all(n in results for n in LOCATION_COMPARISON):
        print("\n--- LOCATION: Skill vs CLAUDE.md ---")
        skill, moved = results["SKILL_NEG"], results["MOVED_NEG"]
        diff = moved.pass_rate - skill.pass_rate
        print(f"  SKILL_NEG: {skill.pass_rate*100:.0f}%  |  MOVED_NEG: {moved.pass_rate*100:.0f}%  |  Diff: {diff*100:+.0f}%")

    # Reiteration
    if all(n in results for n in REITERATION_COMPARISON):
        print("\n--- REITERATION: Skill only vs Both ---")
        skill, reit = results["SKILL_NEG"], results["REITERATE_NEG"]
        diff = reit.pass_rate - skill.pass_rate
        print(f"  SKILL_NEG: {skill.pass_rate*100:.0f}%  |  REITERATE_NEG: {reit.pass_rate*100:.0f}%  |  Diff: {diff*100:+.0f}%")

    # Strategy averages
    neg_cases = [n for n in NEGATIVE_STRATEGY if n in results]
    pos_cases = [n for n in POSITIVE_STRATEGY if n in results]
    if len(neg_cases) > 1 and len(pos_cases) > 1:
        print("\n--- STRATEGY AVERAGES ---")
        neg_avg = sum(results[n].pass_rate for n in neg_cases) / len(neg_cases)
        pos_avg = sum(results[n].pass_rate for n in pos_cases) / len(pos_cases)
        print(f"  Negative avg: {neg_avg*100:.0f}%  |  Positive avg: {pos_avg*100:.0f}%  |  Diff: {(pos_avg-neg_avg)*100:+.0f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Test context impact on LangChain skill following",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-r", "--repetitions", type=int, default=1, help="Runs per case")
    parser.add_argument("-c", "--cases", nargs="+", choices=list(CASES.keys()),
                        help="Specific cases to run")
    parser.add_argument("--compare", choices=list(COMPARISON_GROUPS.keys()),
                        help="Run a comparison group")
    args = parser.parse_args()

    # Determine cases to run
    if args.cases:
        cases_to_run = args.cases
    elif args.compare:
        cases_to_run = COMPARISON_GROUPS[args.compare]
    else:
        cases_to_run = list(CASES.keys())

    print("LANGCHAIN CONTEXT IMPACT TEST")
    print("=" * 60)
    print(f"Cases: {', '.join(cases_to_run)}")
    if args.repetitions > 1:
        print(f"Repetitions: {args.repetitions}")
    if args.model:
        print(f"Model: {args.model}")
    print()

    results = run_cases(cases_to_run, args.repetitions, args.model)
    print_report(results, args.repetitions)

    # Exit code based on results
    if args.repetitions > 1:
        return 0 if any(r.pass_rate > 0 for r in results.values()) else 1
    else:
        return 0 if any(r.passed for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
