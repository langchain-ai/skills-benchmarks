#!/usr/bin/env python3
"""LangChain Agent experiment runner.

Usage:
    .venv/bin/python tests/langchain_agent/test_langchain_agent.py -t BASELINE
    .venv/bin/python tests/langchain_agent/test_langchain_agent.py -t control
    .venv/bin/python tests/langchain_agent/test_langchain_agent.py -t noise
"""

import sys
import argparse
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import (
    run_test, TestResult, verify_environment,
    setup_test_environment, cleanup_test_environment,
    setup_test_context, write_skill, get_noise_skill_content,
)
from tests.langchain_agent.config import (
    TREATMENTS, build_sql_prompt,
    CONTROL_COMPARISON, GUIDANCE_COMPARISON, CLAUDE_MD_COMPARISON,
    NOISE_COMPARISON, NOISE_TREATMENT_COMPARISON,
    MINIMAL_COMPARISON, STRESS_COMPARISON, ALL_TREATMENTS,
)

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
REQUIRED_FILES = ["Dockerfile", "requirements.txt", "chinook.db"]

PRESETS = {
    "control": CONTROL_COMPARISON,
    "guidance": GUIDANCE_COMPARISON,
    "claudemd": CLAUDE_MD_COMPARISON,
    "noise": NOISE_COMPARISON,
    "noise-treatment": NOISE_TREATMENT_COMPARISON,
    "minimal": MINIMAL_COMPARISON,
    "stress": STRESS_COMPARISON,
    "all": ALL_TREATMENTS,
}


def make_test_dir(treatment_name: str) -> Path:
    """Create test directory for a treatment."""
    treatment = TREATMENTS[treatment_name]
    test_dir = setup_test_environment()

    setup_test_context(
        test_dir,
        sections=treatment.sections,
        claude_md=treatment.claude_md,
        environment_dir=ENVIRONMENT_DIR,
    )

    for noise_skill in treatment.noise_tasks:
        content = get_noise_skill_content(noise_skill)
        if content:
            write_skill(test_dir, noise_skill, content)

    return test_dir


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


def run_treatment(name: str, model: str = None) -> TestResult:
    """Run a single treatment."""
    treatment = TREATMENTS[name]
    prompt = build_sql_prompt(treatment, name)
    test_dir = make_test_dir(name)

    print(f"\n[TREATMENT] {name}: {treatment.description}")
    print(f"Noise tasks: {treatment.noise_tasks or 'None'}")
    print(f"CLAUDE.md: {'Yes' if treatment.claude_md else 'No'}")
    print("-" * 50)

    result = run_test(
        name, prompt, test_dir,
        lambda events, td: treatment.validate(events, td),
        timeout=600,
        model=model,
    )

    cleanup_test_environment(test_dir)
    return result


def run_treatments(treatments: list[str], model: str = None) -> Dict[str, TestResult]:
    """Run multiple treatments."""
    results = {}
    for name in treatments:
        print(f"\n{'='*60}")
        results[name] = run_treatment(name, model)
    return results


def print_report(results: Dict[str, TestResult]):
    """Print experiment results summary."""
    print("\n")
    print("=" * 100)
    print("  LANGCHAIN AGENT EXPERIMENT RESULTS")
    print("=" * 100)

    print(f"\n{'Treatment':<20} {'Result':<8} {'Key Checks'}")
    print("-" * 100)

    for name, r in results.items():
        status = "PASS" if r.passed else "FAIL"
        key_checks = [c for c in r.checks_passed[:4]
                      if not c.startswith(("Turns:", "Duration:", "Tool calls:"))]
        checks_str = ", ".join(key_checks)

        if r.checks_failed:
            checks_str = f"FAIL: {r.checks_failed[0][:50]}"

        print(f"{name:<20} {status:<8} {checks_str}")

    print("-" * 100)
    total = len(results)
    passed = sum(1 for r in results.values() if r.passed)
    print(f"\nSummary: {passed}/{total} passed")

    if failed := [r for r in results.values() if not r.passed]:
        print("\nFailed:")
        for r in failed:
            print(f"  {r.name}: {', '.join(r.checks_failed[:2])}")

    print("\n" + "=" * 100)


def main():
    parser = argparse.ArgumentParser(description="LangChain agent experiment")
    parser.add_argument("--model", type=str, help="Model to use")
    parser.add_argument("-t", "--treatments", nargs="+", metavar="NAME",
                        help="Treatments or presets to run")
    args = parser.parse_args()

    if not args.treatments:
        print("Use -t to specify treatments or presets")
        print(f"Presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    # Verify environment before running
    verify_environment(ENVIRONMENT_DIR, REQUIRED_FILES)

    treatments = expand_treatments(args.treatments)
    print(f"LANGCHAIN AGENT EXPERIMENT\n{'='*60}\nTreatments: {', '.join(treatments)}\n")

    results = run_treatments(treatments, args.model)
    print_report(results)

    return 0 if all(r.passed for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
