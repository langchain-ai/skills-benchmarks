#!/usr/bin/env python3
"""Test how documentation quality affects edge case handling."""

import sys
import argparse
import os
from pathlib import Path

skills_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_root))

from scaffold.setup import setup_test_environment, cleanup_test_environment
from scaffold.runner import run_test


MINIMAL_DOCS = """# Trace Query
```python
from langsmith import Client
client = Client()
runs = client.list_runs(project_name="...", limit=10)
for run in runs:
    print(run.trace_id)
```"""

STRUCTURED_DOCS = """# LangSmith Trace Query

## Quick Start
```python
from langsmith import Client
client = Client()
runs = client.list_runs(project_name="my-project", limit=10, is_root=True)
```

## Analyzing Runs
```python
# Convert to list for multiple iterations
runs_list = list(runs)
successful = [r for r in runs_list if r.error is None]
success_rate = len(successful) / len(runs_list) if runs_list else 0

# Calculate latency (check end_time first)
for run in runs_list:
    if run.end_time and run.start_time:
        latency = (run.end_time - run.start_time).total_seconds()
```

## Gotchas
1. Runs is an iterator - use list() for multiple iterations
2. end_time can be None - check before latency calc
3. error is None for success - use `is None` not truthiness"""

VERBOSE_DOCS = """# LangSmith Trace Query - v2.3.1

## Background
LangSmith is a platform for LLM application monitoring...
[many paragraphs of context]

## Prerequisites
1. LANGSMITH_API_KEY set
2. langsmith package installed
3. Network access to api.smith.langchain.com

## API Reference
The Client class provides list_runs() with many parameters:
project_id, project_name, run_type, trace_id, filter, limit, etc.

## Usage
```python
from langsmith import Client
client = Client()
runs = list(client.list_runs(project_name="my-project", limit=10))
successful = [r for r in runs if r.error is None]
```

Note: end_time may be None for incomplete runs. Check before calculating latency.
The runs iterator should be converted to list() for multiple iterations.
Use `error is None` not truthiness to check success."""


PROMPT = """Analyze traces from LangSmith project "skills".

Create trace_analysis.py that:
1. Queries 20 most recent traces
2. Calculates success rate (% without errors)
3. Calculates average latency of successful runs
4. Prints summary: total, successful, failed, rate, avg latency

Use SKILL.md for guidance."""


def validate(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Check for proper edge case handling in generated code."""
    passed, failed = [], []

    f = test_dir / "trace_analysis.py"
    if not f.exists():
        return passed, ["No trace_analysis.py"]

    c = f.read_text()
    passed.append("Created file")

    # Check iterator handling
    if "list(" in c or "runs_list" in c:
        passed.append("Handles iterator")
    else:
        failed.append("May have iterator bug")

    # Check latency null handling
    if ("end_time and" in c or "end_time is not None" in c) and "total_seconds" in c:
        passed.append("Handles None end_time")
    elif "total_seconds" in c:
        failed.append("May crash on None end_time")

    # Check error filtering
    if "error is None" in c or "error is not None" in c:
        passed.append("Correct error check")
    elif "error" in c:
        failed.append("Incorrect error check")

    return passed, failed


def run_with_docs(style: str, docs: str, model: str = None) -> dict:
    test_dir = setup_test_environment()
    (test_dir / "SKILL.md").write_text(docs)

    result = run_test(
        name=f"Docs [{style}]",
        prompt=PROMPT,
        test_dir=test_dir,
        validate=validate,
        model=model,
    )

    cleanup_test_environment(test_dir)
    return {"style": style, "passed": result.passed, "checks": len(result.checks_passed)}


def run(model: str = None):
    print("SKILL DESIGN TEST: Documentation Formats\n")

    results = []
    for style, docs in [("MINIMAL", MINIMAL_DOCS), ("STRUCTURED", STRUCTURED_DOCS), ("VERBOSE", VERBOSE_DOCS)]:
        results.append(run_with_docs(style, docs, model))

    print(f"\n{'='*40}\nCOMPARISON")
    for r in results:
        print(f"  {r['style']:12} {'PASS' if r['passed'] else 'FAIL'} ({r['checks']} checks)")

    best = max(results, key=lambda x: x["checks"])
    print(f"\nBest: {best['style']}")

    return 0 if any(r["passed"] for r in results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    sys.exit(run(model=args.model))
