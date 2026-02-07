#!/usr/bin/env python3
"""Evaluator test runner - executed in Docker to safely run untrusted code.

Usage: python eval_runner.py <evaluator_module> <func_name> <test_cases.json>
Output: Prints "EVALUATOR_RESULTS:<json>" with test results.
"""

import json
import sys
import importlib


def normalize_score(score):
    """Normalize score to 0-1 range."""
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)):
        return float(score) if 0 <= score <= 1 else (score / 100 if score > 1 else 0)
    return 0.0


def extract_score(result):
    """Extract score from result dict.

    LangSmith evaluators return {metric_name: score, "comment": "..."}.
    The metric name is used directly as the key (e.g., "trajectory_match", "accuracy").
    """
    if isinstance(result, (int, float, bool)):
        return result
    if isinstance(result, dict):
        # First check common generic keys
        for key in ["score", "value", "result", "pass", "passed"]:
            if key in result:
                return result[key]
        # Then look for any numeric value (excluding "comment" which is feedback text)
        for key, val in result.items():
            if key != "comment" and isinstance(val, (int, float, bool)):
                return val
    return None


def run_test_case(eval_func, tc):
    """Run single test case, return result dict."""
    name = tc.get("name", "unknown")
    expected = tc.get("expected_result", {})

    try:
        result = eval_func(tc["run"], tc["example"])

        if expected.get("should_not_crash"):
            return {"name": name, "passed": True}

        score = extract_score(result)
        if score is None:
            return {"name": name, "passed": False, "error": "no score"}

        score = normalize_score(score)
        min_s = expected.get("min_score", 0)
        max_s = expected.get("max_score", 1)
        return {"name": name, "passed": min_s <= score <= max_s, "score": score}

    except Exception as e:
        return {"name": name, "passed": False, "error": str(e)[:50]}


def main():
    if len(sys.argv) != 4:
        print("Usage: python eval_runner.py <module> <func> <test_cases.json>", file=sys.stderr)
        sys.exit(1)

    module_name, func_name, test_cases_file = sys.argv[1:4]

    # Import evaluator function
    module = importlib.import_module(module_name)
    eval_func = getattr(module, func_name)

    # Load test cases
    with open(test_cases_file) as f:
        test_cases = json.load(f)

    # Run tests
    results = [run_test_case(eval_func, tc) for tc in test_cases]

    # Output results (parsed by validator)
    print("EVALUATOR_RESULTS:" + json.dumps(results))


if __name__ == "__main__":
    main()
