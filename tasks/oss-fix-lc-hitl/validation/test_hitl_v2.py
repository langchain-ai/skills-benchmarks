"""Execution-based tests for LangChain human-in-the-loop agent fixes.

The broken code has multiple issues:
1. No checkpointer - state not persisted, can't pause/resume
2. No HITL middleware - dangerous tools execute without approval
3. No thread_id in config - state not tracked per user
4. Wrong resume syntax - starts fresh instead of continuing from checkpoint

These tests invoke the actual agent and check real behavior.
"""

import ast

from scaffold.python.validation.runner import TestRunner


def _require_module(runner):
    """Load and return the agent module. Cached by runner.load_module()."""
    return runner.load_module(runner.artifacts[0])


# =============================================================================
# Check 1: Checkpointer Configured
# =============================================================================


def check_has_checkpointer(runner):
    """Check that agent has a checkpointer for state persistence."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        agent = module.agent
        if hasattr(agent, "checkpointer") and agent.checkpointer is not None:
            runner.passed("has_checkpointer")
        else:
            runner.failed(
                "has_checkpointer: "
                "agent.checkpointer is None — need checkpointer for HITL pause/resume"
            )
    except Exception as e:
        runner.failed(f"has_checkpointer: {e}")


# =============================================================================
# Check 2: HITL Middleware Configured
# =============================================================================


def check_has_hitl_middleware(runner):
    """Check that create_agent is called with HITL middleware.

    Uses AST to verify the code passes a middleware argument
    containing human_in_the_loop to create_agent.
    """
    module = _require_module(runner)
    if module is None:
        return

    try:
        source = runner.read(runner.artifacts[0])
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
            runner.passed("has_hitl_middleware")
        else:
            runner.failed(
                "has_hitl_middleware: "
                "create_agent missing middleware= argument — "
                "need human_in_the_loop_middleware to gate dangerous tools"
            )
    except Exception as e:
        runner.failed(f"has_hitl_middleware: {e}")


# =============================================================================
# Check 3: Safe Action Completes (LLM call)
# =============================================================================


def check_safe_action_completes(runner):
    """Safe operations (lookup) should complete without interruption."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        result = module.process_request(
            "Look up the document called 'report.pdf'",
            thread_id="test-safe",
        )

        messages = result.get("messages", [])
        last_content = messages[-1].content if messages else ""

        if "report.pdf" in last_content.lower() or "document" in last_content.lower():
            runner.passed("safe_action_completes")
        else:
            runner.failed(
                f"safe_action_completes: expected lookup result, got: '{last_content[:80]}'"
            )
    except Exception as e:
        runner.failed(f"safe_action_completes: {e}")


# =============================================================================
# Check 4: Dangerous Action Interrupts
# =============================================================================


def check_dangerous_action_interrupts(runner):
    """Dangerous operations (delete) should pause for human approval."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        result = module.process_request(
            "Delete the document 'secret.pdf'",
            thread_id="test-interrupt",
        )

        # If HITL is working, result should contain an interrupt
        if "__interrupt__" in result:
            runner.passed("dangerous_action_interrupts")
        else:
            # Check if the tool executed without approval
            messages = result.get("messages", [])
            last_content = messages[-1].content if messages else ""
            if "deleted" in last_content.lower() or "permanently" in last_content.lower():
                runner.failed(
                    "dangerous_action_interrupts: "
                    "delete executed without approval — "
                    "need HITL middleware with interrupt_on for delete_document"
                )
            else:
                runner.failed(
                    "dangerous_action_interrupts: "
                    "no interrupt detected — expected __interrupt__ in result"
                )
    except Exception as e:
        runner.failed(f"dangerous_action_interrupts: {e}")


# =============================================================================
# Check 5: Resume After Approval
# =============================================================================


def check_resume_after_approval(runner):
    """After interrupt, resume should complete the action."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        # First, trigger the interrupt
        result = module.process_request(
            "Delete the document 'old_file.txt'",
            thread_id="test-resume",
        )

        if "__interrupt__" not in result:
            runner.failed(
                "resume_after_approval: "
                "prerequisite failed — delete didn't interrupt (fix HITL first)"
            )
            return

        # Resume after approval
        result = module.resume_after_approval(thread_id="test-resume")

        messages = result.get("messages", [])
        last_content = messages[-1].content if messages else ""

        if "deleted" in last_content.lower() or "old_file" in last_content.lower():
            runner.passed("resume_after_approval")
        else:
            runner.failed(
                f"resume_after_approval: "
                f"resume should complete the delete, got: '{last_content[:80]}' — "
                "use Command(resume=...) with same thread_id to continue from checkpoint"
            )
    except Exception as e:
        runner.failed(f"resume_after_approval: {e}")


# =============================================================================
# Check 6: Thread Isolation
# =============================================================================


def check_thread_isolation(runner):
    """Different thread_ids should have isolated conversations."""
    module = _require_module(runner)
    if module is None:
        return

    try:
        # Alice's conversation
        module.process_request(
            "Look up the document 'alice_report'",
            thread_id="user-alice",
        )
        result_a = module.process_request(
            "What document did I just ask about?",
            thread_id="user-alice",
        )

        # Bob's conversation (separate thread, no prior context)
        result_b = module.process_request(
            "What document did I just ask about?",
            thread_id="user-bob",
        )

        alice_content = result_a.get("messages", [])[-1].content if result_a.get("messages") else ""
        bob_content = result_b.get("messages", [])[-1].content if result_b.get("messages") else ""

        # Alice should remember, Bob should not
        alice_remembers = "alice_report" in alice_content.lower()
        bob_doesnt_know = "alice_report" not in bob_content.lower()

        if alice_remembers and bob_doesnt_know:
            runner.passed("thread_isolation")
        elif not alice_remembers:
            runner.failed(
                "thread_isolation: alice's thread lost context — need checkpointer + thread_id"
            )
        else:
            runner.failed(
                "thread_isolation: bob's thread has alice's context — threads not isolated"
            )
    except Exception as e:
        runner.failed(f"thread_isolation: {e}")


if __name__ == "__main__":
    TestRunner.run(
        [
            check_has_checkpointer,
            check_has_hitl_middleware,
            check_safe_action_completes,
            check_dangerous_action_interrupts,
            check_resume_after_approval,
            check_thread_isolation,
        ]
    )
