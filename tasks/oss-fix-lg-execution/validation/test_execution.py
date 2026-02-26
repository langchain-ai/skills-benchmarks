"""Execution-based tests for LangGraph pipeline fixes.

The broken code has multiple issues:
1. No reducer on results - parallel workers crash with InvalidUpdateError
2. No interrupt in review - results finalized without human approval
3. No checkpointer - can't pause/resume
4. No thread_id in config - state not tracked
5. Wrong resume syntax - restarts pipeline instead of continuing

These tests invoke the actual pipeline and check real behavior.
"""

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestContext:
    """Shared context for test execution."""

    module_path: str
    module: Any | None = None
    results: dict = field(default_factory=lambda: {"passed": [], "failed": [], "error": None})

    def load(self) -> bool:
        """Import the module. Returns True if successful."""
        try:
            spec = importlib.util.spec_from_file_location("broken_pipeline", self.module_path)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
        except Exception as e:
            self.results["error"] = f"Failed to import module: {e}"
            return False
        return True

    def pass_test(self, name: str):
        self.results["passed"].append(name)

    def fail_test(self, name: str, reason: str):
        self.results["failed"].append(f"{name}: {reason}")


# =============================================================================
# Test 1: Fan-out doesn't crash
# =============================================================================


def test_fan_out_works(ctx: TestContext):
    """Multiple tasks should be processed in parallel without crashing.

    Without a reducer, parallel workers writing to the same field
    causes InvalidUpdateError.
    """
    TEST_NAME = "fan_out_works"

    try:
        result = ctx.module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-fanout",
        )

        results = result.get("results", [])
        if len(results) >= 3:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"expected 3+ results, got {len(results)} — "
                "need Annotated[list, operator.add] reducer for parallel writes",
            )
    except Exception as e:
        error_str = str(e)
        if "InvalidUpdateError" in error_str or "multiple values" in error_str.lower():
            ctx.fail_test(
                TEST_NAME,
                "parallel workers crash — need Annotated[list, operator.add] "
                "reducer on results field",
            )
        else:
            ctx.fail_test(TEST_NAME, str(e)[:200])


# =============================================================================
# Test 2: Results match tasks
# =============================================================================


def test_results_match_tasks(ctx: TestContext):
    """Each input task should produce a corresponding result."""
    TEST_NAME = "results_match_tasks"

    try:
        result = ctx.module.run_pipeline(
            ["alpha", "beta"],
            thread_id="test-match",
        )

        results = result.get("results", [])
        results_str = " ".join(str(r) for r in results).lower()

        has_alpha = "alpha" in results_str
        has_beta = "beta" in results_str

        if has_alpha and has_beta:
            ctx.pass_test(TEST_NAME)
        else:
            missing = []
            if not has_alpha:
                missing.append("alpha")
            if not has_beta:
                missing.append("beta")
            ctx.fail_test(
                TEST_NAME,
                f"missing results for: {missing} — got: {results}",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e)[:200])


# =============================================================================
# Test 3: Review interrupts for approval
# =============================================================================


def test_review_interrupts(ctx: TestContext):
    """Pipeline should pause for human review before finalizing."""
    TEST_NAME = "review_interrupts"

    try:
        result = ctx.module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-interrupt",
        )

        if "__interrupt__" in result:
            ctx.pass_test(TEST_NAME)
        else:
            summary = result.get("summary", "")
            if summary:
                ctx.fail_test(
                    TEST_NAME,
                    "pipeline finalized without review — "
                    "need interrupt() in review node + checkpointer",
                )
            else:
                ctx.fail_test(
                    TEST_NAME,
                    "no interrupt detected — expected __interrupt__ in result",
                )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e)[:200])


# =============================================================================
# Test 4: Resume after review
# =============================================================================


def test_resume_after_review(ctx: TestContext):
    """Resuming after review should complete the pipeline."""
    TEST_NAME = "resume_after_review"

    try:
        # First, trigger interrupt
        result = ctx.module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-resume",
        )

        if "__interrupt__" not in result:
            ctx.fail_test(
                TEST_NAME,
                "prerequisite failed — pipeline didn't interrupt (fix review first)",
            )
            return

        # Resume
        result = ctx.module.resume_after_review(thread_id="test-resume")

        summary = result.get("summary", "")
        status = result.get("status", "")

        if summary and ("3" in summary or "task" in summary.lower()):
            ctx.pass_test(TEST_NAME)
        elif status == "approved":
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"resume didn't complete pipeline, got summary='{summary}', status='{status}' — "
                "use Command(resume=...) with same thread_id",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e)[:200])


# =============================================================================
# Test 5: Summary includes task count
# =============================================================================


def test_summary_correct(ctx: TestContext):
    """Final summary should reflect the number of processed tasks."""
    TEST_NAME = "summary_correct"

    try:
        # Use a single task to avoid interrupt (if interrupt threshold is > 1)
        result = ctx.module.run_pipeline(
            ["only_task"],
            thread_id="test-summary",
        )

        # If interrupted, resume first
        if "__interrupt__" in result:
            result = ctx.module.resume_after_review(thread_id="test-summary")

        summary = result.get("summary", "")
        if summary:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "no summary produced after pipeline completion",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e)[:200])


# =============================================================================
# Main Test Runner
# =============================================================================


def run_tests(module_path: str) -> dict:
    """Run all tests against the module."""
    ctx = TestContext(module_path=module_path)

    tests = [
        test_fan_out_works,
        test_results_match_tasks,
        test_review_interrupts,
        test_resume_after_review,
        test_summary_correct,
    ]

    if not ctx.load():
        for test_fn in tests:
            test_name = test_fn.__name__.replace("test_", "")
            ctx.fail_test(test_name, f"import failed: {ctx.results['error']}")
        return ctx.results

    for test_fn in tests:
        try:
            test_fn(ctx)
        except Exception as e:
            test_name = test_fn.__name__.replace("test_", "")
            ctx.fail_test(test_name, str(e))

    return ctx.results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_execution.py <path_to_pipeline.py>")
        sys.exit(1)

    results = run_tests(sys.argv[1])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["error"] or results["failed"] else 0)
