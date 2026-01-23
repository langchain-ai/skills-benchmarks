#!/usr/bin/env python3
"""
Claude Code Skill Benchmarks - Test Suite

Runs tests to measure skill design effectiveness:

1. BASELINE TESTS - Raw Claude Code capability (no context)
2. CONTEXT IMPACT - Compare with/without CLAUDE.md
3. SKILL DESIGN - Compare documentation formats
4. SYNERGY TESTS - Multi-skill combinations

Usage:
    uv run python tests/run_test_suite.py
    uv run python tests/run_test_suite.py --model opus
    uv run python tests/run_test_suite.py --category context_impact
    uv run python tests/run_test_suite.py --fast        # Use haiku + short timeouts
    uv run python tests/run_test_suite.py --parallel    # Run tests in parallel
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scaffold.cleanup import cleanup_langsmith_assets


# Test categories and their tests
TEST_CATEGORIES = {
    "baseline": {
        "description": "Raw capability tests (no context)",
        "tests": [
            {
                "name": "SQL Agent (Baseline)",
                "description": "Build SQL agent without any skill context",
                "path": project_root / "tests" / "baseline" / "test_sql_agent.py"
            }
        ]
    },
    "context_impact": {
        "description": "Measure CLAUDE.md impact on performance",
        "tests": [
            {
                "name": "CLAUDE.md Impact",
                "description": "Compare performance with/without CLAUDE.md",
                "path": project_root / "tests" / "context_impact" / "test_claude_md_impact.py"
            }
        ]
    },
    "skill_design": {
        "description": "Compare skill documentation formats",
        "tests": [
            {
                "name": "Trace Analysis Docs",
                "description": "Edge case handling with different doc styles",
                "path": project_root / "tests" / "skill_design" / "test_documentation_formats.py"
            },
            {
                "name": "Pytest Fixtures",
                "description": "Pattern adherence with minimal vs structured docs",
                "path": project_root / "tests" / "skill_design" / "test_pytest_fixtures.py"
            }
        ]
    },
    "synergy": {
        "description": "Multi-skill combination tests",
        "tests": [
            {
                "name": "Build-Trace-Dataset Pipeline",
                "description": "Chain multiple skills together",
                "path": project_root / "tests" / "synergy" / "test_build_trace_dataset.py"
            }
        ]
    }
}


def run_test_script(test_path: Path, model: str = None, quiet: bool = False) -> tuple:
    """Run a test script as a subprocess.

    Returns:
        Tuple of (return_code, stdout) for analysis
    """
    cmd = ["uv", "run", "python", str(test_path)]
    if model:
        cmd.extend(["--model", model])

    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=quiet,
        text=True
    )
    return result.returncode, result.stdout if quiet else ""


def run_single_test(test: dict, model: str = None, quiet: bool = False) -> tuple:
    """Run a single test. Returns (name, returncode, stdout)."""
    if not test["path"].exists():
        return (test["name"], -1, "Test file not found")

    returncode, stdout = run_test_script(test["path"], model, quiet)
    return (test["name"], returncode, stdout)


def run_category(category: str, model: str = None, parallel: bool = False, quiet: bool = False) -> list:
    """Run all tests in a category."""
    if category not in TEST_CATEGORIES:
        print(f"Unknown category: {category}")
        return []

    cat_info = TEST_CATEGORIES[category]
    tests = cat_info["tests"]

    if not quiet:
        print(f"\n[{category.upper()}] {cat_info['description']}")

    results = []

    if parallel and len(tests) > 1:
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(run_single_test, test, model, True): test
                for test in tests
            }
            for future in as_completed(futures):
                name, returncode, _ = future.result()
                status = "PASS" if returncode == 0 else "FAIL" if returncode > 0 else "SKIP"
                print(f"  {status}: {name}")
                results.append((name, returncode))
    else:
        # Run tests sequentially
        for test in tests:
            if not quiet:
                print(f"  Running: {test['name']}...", end=" ", flush=True)

            name, returncode, _ = run_single_test(test, model, quiet)
            status = "PASS" if returncode == 0 else "FAIL" if returncode > 0 else "SKIP"

            if quiet:
                print(f"  {status}: {name}")
            else:
                print(status)

            results.append((name, returncode))

    return results


def run_suite(categories: list = None, model: str = None, parallel: bool = False, quiet: bool = False):
    """Run the test suite."""
    start_time = datetime.now()

    if not quiet:
        print(f"CLAUDE CODE SKILL BENCHMARKS | {start_time.strftime('%H:%M:%S')} | model={model or 'default'}")

    # Default to all categories
    if not categories:
        categories = list(TEST_CATEGORIES.keys())

    all_results = {}

    for category in categories:
        results = run_category(category, model, parallel, quiet)
        all_results[category] = results

    # Print summary
    duration = (datetime.now() - start_time).total_seconds()

    total_passed = sum(1 for r in sum(all_results.values(), []) if r[1] == 0)
    total_failed = sum(1 for r in sum(all_results.values(), []) if r[1] > 0)

    print(f"\n{'='*50}")
    print(f"RESULTS: {total_passed} passed, {total_failed} failed | {duration:.0f}s")

    if total_failed > 0:
        print("\nFailed tests:")
        for category, results in all_results.items():
            for name, result in results:
                if result > 0:
                    print(f"  - {category}/{name}")

    print(f"{'='*50}")
    return 0 if total_failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Run Claude Code skill benchmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run all tests
  %(prog)s --fast             # Quick run with haiku model
  %(prog)s --parallel         # Run tests in parallel
  %(prog)s --category baseline
"""
    )
    parser.add_argument("--model", type=str, help="Model (default: sonnet)")
    parser.add_argument("--category", action="append", dest="categories", help="Category to run")
    parser.add_argument("--fast", action="store_true", help="Fast mode: use haiku model")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--quiet", "-q", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--list", action="store_true", help="List test categories")

    args = parser.parse_args()

    if args.list:
        print("Categories:")
        for cat, info in TEST_CATEGORIES.items():
            tests = ", ".join(t["name"] for t in info["tests"])
            print(f"  {cat}: {tests}")
        return 0

    model = args.model or ("haiku" if args.fast else None)
    return run_suite(
        categories=args.categories,
        model=model,
        parallel=args.parallel,
        quiet=args.quiet
    )


if __name__ == "__main__":
    sys.exit(main())
