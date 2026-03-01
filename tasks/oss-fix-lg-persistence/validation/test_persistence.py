"""Execution-based tests for LangGraph persistence and state fixes.

The broken code has multiple issues:
1. No checkpointer - state not saved between invocations
2. No thread_id usage - conversations not isolated
3. Missing reducer on messages list - messages get overwritten, not accumulated
4. Node returns entire state instead of partial update dict

These tests verify the code actually works, not just that it contains patterns.
"""

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from typing import Any

from scaffold.python.validation.core import write_test_results


@dataclass
class TestContext:
    """Shared context for test execution."""

    module_path: str
    module: Any | None = None
    graph: Any | None = None
    results: dict = field(default_factory=lambda: {"passed": [], "failed": [], "error": None})

    def load(self) -> bool:
        """Load module and graph. Returns True if successful."""
        try:
            spec = importlib.util.spec_from_file_location("agent", self.module_path)
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)
            self.graph = self.module.graph
        except Exception as e:
            self.results["error"] = f"Failed to import agent: {e}"
            return False
        return True

    def pass_test(self, name: str):
        """Mark a test as passed."""
        self.results["passed"].append(name)

    def fail_test(self, name: str, reason: str):
        """Mark a test as failed with reason."""
        self.results["failed"].append(f"{name}: {reason}")


# =============================================================================
# Test 1: Checkpointer Configured
# =============================================================================


def test_has_checkpointer(ctx: TestContext):
    """Check that graph has a checkpointer configured.

    Without a checkpointer, state is lost between invocations.
    """
    TEST_NAME = "has_checkpointer"

    try:
        if hasattr(ctx.graph, "checkpointer") and ctx.graph.checkpointer is not None:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "graph.checkpointer is None - need to add checkpointer to compile()",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 2: State Persists Across Invocations
# =============================================================================


def test_state_persists(ctx: TestContext):
    """Check that state persists across invocations with thread_id.

    With checkpointer + thread_id, messages should accumulate across calls.
    """
    TEST_NAME = "state_persists_across_calls"

    try:
        config = {"configurable": {"thread_id": "test-persistence"}}

        # First invoke
        result1 = ctx.graph.invoke(
            {"messages": ["Hello"], "context": {}, "current_step": "start"}, config
        )
        msgs_after_1 = len(result1.get("messages", []))

        # Second invoke - should accumulate
        result2 = ctx.graph.invoke(
            {"messages": ["How are you?"], "context": {}, "current_step": "start"}, config
        )
        msgs_after_2 = len(result2.get("messages", []))

        if msgs_after_2 > msgs_after_1:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"messages didn't accumulate (call 1: {msgs_after_1}, call 2: {msgs_after_2}) - "
                "need checkpointer + thread_id",
            )
    except ValueError as e:
        ctx.fail_test(TEST_NAME, str(e))
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 3: Messages Accumulate (Reducer Test)
# =============================================================================


def test_messages_accumulate(ctx: TestContext):
    """Check that messages accumulate within single invocation.

    With proper reducer (Annotated[list, operator.add]), messages should
    accumulate: input message + response.
    """
    TEST_NAME = "messages_accumulate_with_reducer"

    try:
        config = {"configurable": {"thread_id": "test-reducer"}}

        # Invoke with a message - should go through extract -> respond
        # and accumulate the response to the messages list
        result = ctx.graph.invoke(
            {"messages": ["Test message"], "context": {}, "current_step": "start"}, config
        )

        messages = result.get("messages", [])
        # With proper reducer, should have: input message + response
        if len(messages) >= 2:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"expected >=2 messages, got {len(messages)} - "
                "need Annotated[list, operator.add] reducer",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 4: No Message Duplication
# =============================================================================


def test_no_duplication(ctx: TestContext):
    """Check that nodes return partial updates, not entire state.

    If a node returns the entire state with a reducer, input gets duplicated.
    Nodes should return only the fields they want to update.
    """
    TEST_NAME = "no_message_duplication"

    try:
        config = {"configurable": {"thread_id": "test-no-duplication"}}

        # Single invoke with one message
        result = ctx.graph.invoke(
            {"messages": ["Hello there"], "context": {}, "current_step": "start"}, config
        )

        messages = result.get("messages", [])
        # Should have exactly 2: input + response
        # If a node returns entire state with reducer, input gets duplicated -> 3+ messages
        input_count = sum(1 for m in messages if m == "Hello there")

        if input_count == 1 and len(messages) == 2:
            ctx.pass_test(TEST_NAME)
        elif input_count > 1:
            ctx.fail_test(
                TEST_NAME,
                f"input message duplicated {input_count} times - "
                "node is returning entire state instead of partial update dict",
            )
        else:
            ctx.fail_test(
                TEST_NAME,
                f"unexpected message count {len(messages)}, messages: {messages}",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 5: Bot Remembers Name Across Turns
# =============================================================================


def test_remembers_name(ctx: TestContext):
    """Check that bot remembers user's name across turns.

    This is a functional test - with proper persistence, the bot should
    remember information from earlier in the conversation.
    """
    TEST_NAME = "remembers_user_name"

    try:
        config = {"configurable": {"thread_id": "test-name-memory"}}

        # Introduce ourselves
        ctx.graph.invoke(
            {"messages": ["Hi! My name is Alex"], "context": {}, "current_step": "start"}, config
        )

        # Ask for name
        result = ctx.graph.invoke(
            {"messages": ["What is my name?"], "context": {}, "current_step": "start"}, config
        )

        messages = result.get("messages", [])
        last_response = messages[-1].lower() if messages else ""

        if "alex" in last_response:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"expected 'alex' in response, got: '{messages[-1] if messages else 'no messages'}'",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 6: Thread Isolation
# =============================================================================


def test_thread_isolation(ctx: TestContext):
    """Check that different thread_ids have separate state.

    Different users (threads) should have isolated conversations.
    """
    TEST_NAME = "thread_isolation"

    try:
        config_a = {"configurable": {"thread_id": "user-alice"}}
        config_b = {"configurable": {"thread_id": "user-bob"}}

        # Alice's conversation
        ctx.graph.invoke(
            {"messages": ["My name is Alice"], "context": {}, "current_step": "start"}, config_a
        )
        ctx.graph.invoke(
            {"messages": ["More from Alice"], "context": {}, "current_step": "start"}, config_a
        )
        result_a = ctx.graph.invoke(
            {"messages": ["Alice again"], "context": {}, "current_step": "start"}, config_a
        )

        # Bob's conversation (separate)
        result_b = ctx.graph.invoke(
            {"messages": ["My name is Bob"], "context": {}, "current_step": "start"}, config_b
        )

        alice_msgs = len(result_a.get("messages", []))
        bob_msgs = len(result_b.get("messages", []))

        if bob_msgs < alice_msgs:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"threads not isolated (Alice: {alice_msgs}, Bob: {bob_msgs})",
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

    # Run each test
    tests = [
        test_has_checkpointer,
        test_state_persists,
        test_messages_accumulate,
        test_no_duplication,
        test_remembers_name,
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
        print("Usage: python test_persistence.py <path_to_agent.py>")
        sys.exit(1)

    agent_path = sys.argv[1]
    results = run_tests(agent_path)

    print(json.dumps(results, indent=2))
    write_test_results(results)

    if results["error"] or results["failed"]:
        sys.exit(1)
    sys.exit(0)
