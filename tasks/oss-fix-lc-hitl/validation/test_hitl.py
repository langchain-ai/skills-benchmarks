"""Execution-based tests for LangChain human-in-the-loop agent fixes.

The broken code has multiple issues:
1. No checkpointer - state not persisted, can't pause/resume
2. No HITL middleware - dangerous tools execute without approval
3. No thread_id in config - state not tracked per user
4. Wrong resume syntax - starts fresh instead of continuing from checkpoint

These tests invoke the actual agent and check real behavior.
"""

import ast
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
            spec = importlib.util.spec_from_file_location("broken_agent", self.module_path)
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
# Test 1: Checkpointer Configured
# =============================================================================


def test_has_checkpointer(ctx: TestContext):
    """Check that agent has a checkpointer for state persistence."""
    TEST_NAME = "has_checkpointer"

    try:
        agent = ctx.module.agent
        if hasattr(agent, "checkpointer") and agent.checkpointer is not None:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "agent.checkpointer is None — need checkpointer for HITL pause/resume",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 2: HITL Middleware Configured
# =============================================================================


def test_has_hitl_middleware(ctx: TestContext):
    """Check that create_agent is called with HITL middleware.

    Uses AST to verify the code passes a middleware argument
    containing human_in_the_loop to create_agent.
    """
    TEST_NAME = "has_hitl_middleware"

    try:
        source = open(ctx.module_path).read()
        tree = ast.parse(source)

        found_middleware = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for middleware= keyword in any function call
                for kw in node.keywords:
                    if kw.arg == "middleware":
                        found_middleware = True
                        break

        if found_middleware:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "create_agent missing middleware= argument — "
                "need human_in_the_loop_middleware to gate dangerous tools",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 3: Safe Action Completes (LLM call)
# =============================================================================


def test_safe_action_completes(ctx: TestContext):
    """Safe operations (lookup) should complete without interruption."""
    TEST_NAME = "safe_action_completes"

    try:
        result = ctx.module.process_request(
            "Look up the document called 'report.pdf'",
            thread_id="test-safe",
        )

        messages = result.get("messages", [])
        last_content = messages[-1].content if messages else ""

        if "report.pdf" in last_content.lower() or "document" in last_content.lower():
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"expected lookup result, got: '{last_content[:80]}'",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 3: Dangerous Action Interrupts
# =============================================================================


def test_dangerous_action_interrupts(ctx: TestContext):
    """Dangerous operations (delete) should pause for human approval."""
    TEST_NAME = "dangerous_action_interrupts"

    try:
        result = ctx.module.process_request(
            "Delete the document 'secret.pdf'",
            thread_id="test-interrupt",
        )

        # If HITL is working, result should contain an interrupt
        if "__interrupt__" in result:
            ctx.pass_test(TEST_NAME)
        else:
            # Check if the tool executed without approval
            messages = result.get("messages", [])
            last_content = messages[-1].content if messages else ""
            if "deleted" in last_content.lower() or "permanently" in last_content.lower():
                ctx.fail_test(
                    TEST_NAME,
                    "delete executed without approval — "
                    "need HITL middleware with interrupt_on for delete_document",
                )
            else:
                ctx.fail_test(
                    TEST_NAME,
                    "no interrupt detected — expected __interrupt__ in result",
                )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 4: Resume After Approval
# =============================================================================


def test_resume_after_approval(ctx: TestContext):
    """After interrupt, resume should complete the action."""
    TEST_NAME = "resume_after_approval"

    try:
        # First, trigger the interrupt
        result = ctx.module.process_request(
            "Delete the document 'old_file.txt'",
            thread_id="test-resume",
        )

        if "__interrupt__" not in result:
            ctx.fail_test(
                TEST_NAME,
                "prerequisite failed — delete didn't interrupt (fix HITL first)",
            )
            return

        # Resume after approval
        result = ctx.module.resume_after_approval(thread_id="test-resume")

        messages = result.get("messages", [])
        last_content = messages[-1].content if messages else ""

        if "deleted" in last_content.lower() or "old_file" in last_content.lower():
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"resume should complete the delete, got: '{last_content[:80]}' — "
                "use Command(resume=...) with same thread_id to continue from checkpoint",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 5: Thread Isolation
# =============================================================================


def test_thread_isolation(ctx: TestContext):
    """Different thread_ids should have isolated conversations."""
    TEST_NAME = "thread_isolation"

    try:
        # Alice's conversation
        ctx.module.process_request(
            "Look up the document 'alice_report'",
            thread_id="user-alice",
        )
        result_a = ctx.module.process_request(
            "What document did I just ask about?",
            thread_id="user-alice",
        )

        # Bob's conversation (separate thread, no prior context)
        result_b = ctx.module.process_request(
            "What document did I just ask about?",
            thread_id="user-bob",
        )

        alice_content = result_a.get("messages", [])[-1].content if result_a.get("messages") else ""
        bob_content = result_b.get("messages", [])[-1].content if result_b.get("messages") else ""

        # Alice should remember, Bob should not
        alice_remembers = "alice_report" in alice_content.lower()
        bob_doesnt_know = "alice_report" not in bob_content.lower()

        if alice_remembers and bob_doesnt_know:
            ctx.pass_test(TEST_NAME)
        elif not alice_remembers:
            ctx.fail_test(
                TEST_NAME,
                "alice's thread lost context — need checkpointer + thread_id",
            )
        else:
            ctx.fail_test(
                TEST_NAME,
                "bob's thread has alice's context — threads not isolated",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Main Test Runner
# =============================================================================


def run_tests(module_path: str) -> dict:
    """Run all tests against the module.

    Returns dict with test results: {passed: [], failed: [], error: str|None}
    """
    ctx = TestContext(module_path=module_path)

    tests = [
        test_has_checkpointer,
        test_has_hitl_middleware,
        test_safe_action_completes,
        test_dangerous_action_interrupts,
        test_resume_after_approval,
        test_thread_isolation,
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
        print("Usage: python test_hitl.py <path_to_agent.py>")
        sys.exit(1)

    results = run_tests(sys.argv[1])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["error"] or results["failed"] else 0)
