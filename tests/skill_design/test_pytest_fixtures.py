#!/usr/bin/env python3
"""Test if documentation helps with proper fixture patterns."""

import sys
import argparse
from pathlib import Path

skills_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_root))

from scaffold.setup import setup_test_environment, cleanup_test_environment
from scaffold.runner import run_test


MINIMAL_DOCS = """# Pytest Fixtures
```python
import pytest

@pytest.fixture
def my_fixture():
    return "data"
```"""

STRUCTURED_DOCS = (skills_root / "skills" / "pytest-fixtures" / "SKILL.md").read_text()

PROMPT = """Create conftest.py with pytest fixtures for testing an async web API:
1. An async fixture for an API client that connects/disconnects
2. A database session fixture with test isolation
3. A factory fixture for creating test users

Follow best practices for cleanup and isolation. Use SKILL.md for guidance."""


def validate(events: dict, test_dir: Path) -> tuple[list[str], list[str]]:
    """Check for proper fixture patterns."""
    passed, failed = [], []

    f = test_dir / "conftest.py"
    if not f.exists():
        return passed, ["No conftest.py"]

    c = f.read_text()
    passed.append("Created file")

    # Async pattern
    if "async def" in c:
        if "pytest_asyncio" in c:
            passed.append("Correct async pattern")
        else:
            failed.append("Async should use pytest_asyncio")

    # Cleanup pattern
    if "yield" in c:
        passed.append("Uses yield for cleanup")
    elif any(x in c for x in ["close", "cleanup", "disconnect"]):
        failed.append("Cleanup without yield")

    # DB rollback
    if "session" in c.lower() or "db" in c.lower():
        if "rollback" in c:
            passed.append("DB uses rollback")

    return passed, failed


def run_with_docs(style: str, docs: str, model: str = None) -> dict:
    test_dir = setup_test_environment()
    (test_dir / "SKILL.md").write_text(docs)

    result = run_test(
        name=f"Fixtures [{style}]",
        prompt=PROMPT,
        test_dir=test_dir,
        validate=validate,
        model=model,
    )

    cleanup_test_environment(test_dir)
    return {"style": style, "passed": result.passed, "checks": len(result.checks_passed)}


def run(model: str = None):
    print("SKILL DESIGN TEST: Pytest Fixtures\n")

    results = []
    for style, docs in [("MINIMAL", MINIMAL_DOCS), ("STRUCTURED", STRUCTURED_DOCS)]:
        results.append(run_with_docs(style, docs, model))

    print(f"\n{'='*40}\nCOMPARISON")
    for r in results:
        print(f"  {r['style']:12} {'PASS' if r['passed'] else 'FAIL'} ({r['checks']} checks)")

    diff = results[1]["checks"] - results[0]["checks"]
    print(f"\nStructured {'>' if diff > 0 else '=' if diff == 0 else '<'} Minimal by {abs(diff)}")

    return 0 if any(r["passed"] for r in results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()
    sys.exit(run(model=args.model))
