#!/usr/bin/env python3
"""Evaluator test runner - executed in Docker to safely run untrusted code.

Usage: python eval_runner.py <evaluator_module> <func_name> <test_cases.json> [dataset.json]
Output: Prints "EVALUATOR_RESULTS:<json>" with test results.

If dataset.json is provided and has valid trajectory format, generates test cases
dynamically. Otherwise falls back to test_cases.json.
"""

import importlib
import json
import sys
from pathlib import Path


def normalize_score(score):
    """Normalize score to 0-1 range."""
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)):
        return float(score) if 0 <= score <= 1 else (score / 100 if score > 1 else 0)
    return 0.0


def extract_score(result):
    """Extract score from result dict."""
    if isinstance(result, (int, float, bool)):
        return result
    if isinstance(result, dict):
        for key in ["score", "value", "result", "pass", "passed"]:
            if key in result:
                return result[key]
        for key, val in result.items():
            if key != "comment" and isinstance(val, (int, float, bool)):
                return val
    return None


def get_trajectory(ex: dict) -> list:
    """Extract trajectory from example, handling various formats."""
    if not isinstance(ex, dict):
        return []

    FIELDS = ["expected_trajectory", "trajectory", "expected_tools", "tool_calls", "tools"]

    # Check top-level fields
    for field in FIELDS:
        val = ex.get(field)
        if isinstance(val, list) and val:
            return _normalize_trajectory(val)

    # Check nested in outputs/output
    for container in ["outputs", "output"]:
        outputs = ex.get(container, {})
        if isinstance(outputs, dict):
            for field in FIELDS:
                val = outputs.get(field)
                if isinstance(val, list) and val:
                    return _normalize_trajectory(val)

    return []


def _normalize_trajectory(traj: list) -> list:
    """Normalize trajectory to list of strings."""
    if not traj:
        return []
    if isinstance(traj[0], str):
        return traj
    if isinstance(traj[0], dict):
        return [item.get("name") or item.get("tool") for item in traj if isinstance(item, dict)]
    return []


def normalize_trajectory_fields(data: dict) -> dict:
    """Add trajectory data under multiple field names so evaluators find it."""
    if not isinstance(data, dict) or not isinstance(data.get("outputs"), dict):
        return data

    outputs = data["outputs"]
    FIELDS = ["expected_trajectory", "trajectory", "tool_calls", "tools"]

    traj = next((outputs[f] for f in FIELDS if f in outputs and isinstance(outputs[f], list)), None)
    if not traj:
        traj = next(
            (v for v in outputs.values() if isinstance(v, list) and v and isinstance(v[0], str)),
            None,
        )

    if traj:
        for f in FIELDS:
            outputs.setdefault(f, traj)
    return data


def generate_test_cases_from_dataset(dataset_path: str) -> list:
    """Generate test cases from dataset if it has valid trajectory format."""
    try:
        with open(dataset_path) as f:
            data = json.load(f)

        # Extract examples
        if isinstance(data, list):
            examples = data
        elif isinstance(data, dict):
            examples = data.get("examples", data.get("data", [data]))
        else:
            return None

        if not examples:
            return None

        # Find first example with valid trajectory
        template = None
        trajectory = None
        for ex in examples:
            traj = get_trajectory(ex)
            if traj:
                template = ex
                trajectory = traj
                break

        if not template or not trajectory:
            return None

        # Generate test cases
        def modify_trajectory(new_traj: list) -> dict:
            modified = json.loads(json.dumps(template))
            outputs = modified.get("outputs") or modified.get("output") or {}
            for field in ["expected_trajectory", "trajectory", "tools", "tool_calls"]:
                if field in outputs:
                    outputs[field] = new_traj
                    return modified
            outputs["expected_trajectory"] = new_traj
            return modified

        return [
            {
                "name": "perfect_match",
                "description": "Identical trajectory should score high",
                "run": json.loads(json.dumps(template)),
                "example": template,
                "expected_result": {"should_pass": True, "min_score": 0.9},
            },
            {
                "name": "partial_match",
                "description": "Partial tool overlap should score medium",
                "run": modify_trajectory(trajectory[:1] if len(trajectory) > 1 else trajectory),
                "example": template,
                "expected_result": {"should_pass": True, "min_score": 0.1, "max_score": 0.95},
            },
            {
                "name": "no_match",
                "description": "Different trajectory should score low",
                "run": modify_trajectory(["unknown_tool_xyz"]),
                "example": template,
                "expected_result": {"should_pass": True, "max_score": 0.5},
            },
            {
                "name": "empty_trajectory",
                "description": "Empty trajectory should not crash",
                "run": modify_trajectory([]),
                "example": template,
                "expected_result": {"should_not_crash": True},
            },
        ]
    except Exception:
        return None


def run_test_case(eval_func, tc):
    """Run single test case, return result dict."""
    name = tc.get("name", "unknown")
    expected = tc.get("expected_result", {})

    run = normalize_trajectory_fields(tc.get("run", {}))
    example = normalize_trajectory_fields(tc.get("example", {}))

    try:
        result = eval_func(run, example)

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
    if len(sys.argv) < 4:
        print(
            "Usage: python eval_runner.py <module> <func> <test_cases.json> [dataset.json]",
            file=sys.stderr,
        )
        sys.exit(1)

    module_name, func_name, test_cases_file = sys.argv[1:4]
    dataset_file = sys.argv[4] if len(sys.argv) > 4 else None

    # Add script directory to path so evaluator module can be imported
    script_dir = str(Path(__file__).parent.resolve())
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Import evaluator function
    module = importlib.import_module(module_name)
    eval_func = getattr(module, func_name)

    # Try to generate test cases from dataset, fall back to test_cases_file
    test_cases = None
    if dataset_file and Path(dataset_file).exists():
        test_cases = generate_test_cases_from_dataset(dataset_file)

    if not test_cases:
        with open(test_cases_file) as f:
            test_cases = json.load(f)

    # Run tests
    results = [run_test_case(eval_func, tc) for tc in test_cases]

    # Output in standard format for run_eval_in_docker
    passed_count = sum(1 for r in results if r.get("passed"))
    total = len(results)
    passed = []
    failed = []
    msg = f"Evaluator logic: {passed_count}/{total} tests"
    if passed_count == total:
        passed.append(msg + " passed")
    elif passed_count > total // 2:
        passed.append(msg + " (partial)")
    else:
        failed.append(msg + " passed")

    print(json.dumps({"passed": passed, "failed": failed, "error": None}))


if __name__ == "__main__":
    main()
