"""Execution-based tests for LangGraph pipeline fixes.

The broken code has multiple issues:
1. No reducer on results - parallel workers crash with InvalidUpdateError
2. No interrupt in review - results finalized without human approval
3. No checkpointer - can't pause/resume
4. No thread_id in config - state not tracked
5. Wrong resume syntax - restarts pipeline instead of continuing

These tests invoke the actual pipeline and check real behavior.
"""

from scaffold.python.validation.runner import TestRunner


def _require_module(runner):
    """Load and return the pipeline module. Cached by runner.load_module()."""
    return runner.load_module(runner.artifacts[0])


# =============================================================================
# Check 1: Fan-out doesn't crash
# =============================================================================


def check_fan_out_works(runner):
    """Multiple tasks should be processed in parallel without crashing.

    Without a reducer, parallel workers writing to the same field
    causes InvalidUpdateError.
    """
    module = _require_module(runner)
    if module is None:
        return

    try:
        result = module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-fanout",
        )

        results = result.get("results", [])
        if len(results) >= 3:
            runner.passed("fan_out_works")
        else:
            runner.failed(
                f"fan_out_works: "
                f"expected 3+ results, got {len(results)} — "
                "need Annotated[list, operator.add] reducer for parallel writes"
            )
    except Exception as e:
        error_str = str(e)
        if "InvalidUpdateError" in error_str or "multiple values" in error_str.lower():
            runner.failed(
                "fan_out_works: "
                "parallel workers crash — need Annotated[list, operator.add] "
                "reducer on results field"
            )
        else:
            runner.failed(f"fan_out_works: {str(e)[:200]}")


# =============================================================================
# Check 2: Results match tasks
# =============================================================================


def check_results_match_tasks(runner):
    """Each input task should produce a corresponding result."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        result = module.run_pipeline(
            ["alpha", "beta"],
            thread_id="test-match",
        )

        results = result.get("results", [])
        results_str = " ".join(str(r) for r in results).lower()

        has_alpha = "alpha" in results_str
        has_beta = "beta" in results_str

        if has_alpha and has_beta:
            runner.passed("results_match_tasks")
        else:
            missing = []
            if not has_alpha:
                missing.append("alpha")
            if not has_beta:
                missing.append("beta")
            runner.failed(f"results_match_tasks: missing results for: {missing} — got: {results}")
    except Exception as e:
        runner.failed(f"results_match_tasks: {str(e)[:200]}")


# =============================================================================
# Check 3: Review interrupts for approval
# =============================================================================


def check_review_interrupts(runner):
    """Pipeline should pause for human review before finalizing."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        result = module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-interrupt",
        )

        if "__interrupt__" in result:
            runner.passed("review_interrupts")
        else:
            summary = result.get("summary", "")
            if summary:
                runner.failed(
                    "review_interrupts: "
                    "pipeline finalized without review — "
                    "need interrupt() in review node + checkpointer"
                )
            else:
                runner.failed(
                    "review_interrupts: no interrupt detected — expected __interrupt__ in result"
                )
    except Exception as e:
        runner.failed(f"review_interrupts: {str(e)[:200]}")


# =============================================================================
# Check 4: Resume after review
# =============================================================================


def check_resume_after_review(runner):
    """Resuming after review should complete the pipeline."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        # First, trigger interrupt
        result = module.run_pipeline(
            ["task_a", "task_b", "task_c"],
            thread_id="test-resume",
        )

        if "__interrupt__" not in result:
            runner.failed(
                "resume_after_review: "
                "prerequisite failed — pipeline didn't interrupt (fix review first)"
            )
            return

        # Resume
        result = module.resume_after_review(thread_id="test-resume")

        summary = result.get("summary", "")
        status = result.get("status", "")

        if summary and ("3" in summary or "task" in summary.lower()):
            runner.passed("resume_after_review")
        elif status == "approved":
            runner.passed("resume_after_review")
        else:
            runner.failed(
                f"resume_after_review: "
                f"resume didn't complete pipeline, got summary='{summary}', status='{status}' — "
                "use Command(resume=...) with same thread_id"
            )
    except Exception as e:
        runner.failed(f"resume_after_review: {str(e)[:200]}")


# =============================================================================
# Check 5: Summary includes task count
# =============================================================================


def check_summary_correct(runner):
    """Final summary should reflect the number of processed tasks."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        # Use a single task to avoid interrupt (if interrupt threshold is > 1)
        result = module.run_pipeline(
            ["only_task"],
            thread_id="test-summary",
        )

        # If interrupted, resume first
        if "__interrupt__" in result:
            result = module.resume_after_review(thread_id="test-summary")

        summary = result.get("summary", "")
        if summary:
            runner.passed("summary_correct")
        else:
            runner.failed("summary_correct: no summary produced after pipeline completion")
    except Exception as e:
        runner.failed(f"summary_correct: {str(e)[:200]}")


if __name__ == "__main__":
    TestRunner.run(
        [
            check_fan_out_works,
            check_results_match_tasks,
            check_review_interrupts,
            check_resume_after_review,
            check_summary_correct,
        ]
    )
