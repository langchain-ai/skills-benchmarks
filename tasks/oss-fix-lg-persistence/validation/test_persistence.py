"""Execution-based tests for LangGraph persistence and state fixes.

The broken code has multiple issues:
1. No checkpointer - state not saved between invocations
2. No thread_id usage - conversations not isolated
3. Missing reducer on messages list - messages get overwritten, not accumulated

These tests verify the code actually works, not just that it contains patterns.
"""

import sys
import json


def run_tests(agent_module_path: str) -> dict:
    """Run tests against the agent.

    Returns dict with test results:
    {
        "passed": ["test_name", ...],
        "failed": ["test_name: reason", ...],
        "error": "error message if import failed"
    }
    """
    results = {"passed": [], "failed": [], "error": None}

    # Try to import the agent module
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("agent", agent_module_path)
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)
    except Exception as e:
        results["error"] = f"Failed to import agent: {e}"
        return results

    # Test 1: Graph has checkpointer configured
    try:
        graph = agent.graph
        if hasattr(graph, "checkpointer") and graph.checkpointer is not None:
            results["passed"].append("has_checkpointer")
        else:
            results["failed"].append(
                "has_checkpointer: graph.checkpointer is None - "
                "need to add checkpointer to compile()"
            )
    except Exception as e:
        results["failed"].append(f"has_checkpointer: {e}")

    # Test 2: State persists across invocations with thread_id
    try:
        graph = agent.graph
        config = {"configurable": {"thread_id": "test-persistence"}}

        # First invoke
        result1 = graph.invoke({
            "messages": ["Hello"],
            "context": {},
            "current_step": "start"
        }, config)
        msgs_after_1 = len(result1.get("messages", []))

        # Second invoke - should accumulate
        result2 = graph.invoke({
            "messages": ["How are you?"],
            "context": {},
            "current_step": "start"
        }, config)
        msgs_after_2 = len(result2.get("messages", []))

        if msgs_after_2 > msgs_after_1:
            results["passed"].append("state_persists_across_calls")
        else:
            results["failed"].append(
                f"state_persists_across_calls: messages didn't accumulate "
                f"(call 1: {msgs_after_1}, call 2: {msgs_after_2}) - "
                "need checkpointer + thread_id"
            )
    except ValueError as e:
        if "thread_id" in str(e).lower() or "configurable" in str(e).lower():
            results["failed"].append(
                f"state_persists_across_calls: {e}"
            )
        else:
            results["failed"].append(f"state_persists_across_calls: {e}")
    except Exception as e:
        results["failed"].append(f"state_persists_across_calls: {e}")

    # Test 3: Messages accumulate within single invocation (reducer test)
    try:
        graph = agent.graph
        config = {"configurable": {"thread_id": "test-reducer"}}

        # Invoke with a message - should go through extract -> respond
        # and accumulate the response to the messages list
        result = graph.invoke({
            "messages": ["Test message"],
            "context": {},
            "current_step": "start"
        }, config)

        messages = result.get("messages", [])
        # With proper reducer, should have: input message + response
        if len(messages) >= 2:
            results["passed"].append("messages_accumulate_with_reducer")
        else:
            results["failed"].append(
                f"messages_accumulate_with_reducer: expected >=2 messages, "
                f"got {len(messages)} - need Annotated[list, operator.add] reducer"
            )
    except Exception as e:
        results["failed"].append(f"messages_accumulate_with_reducer: {e}")

    # Test 4: Functional - bot remembers name across turns
    try:
        graph = agent.graph
        config = {"configurable": {"thread_id": "test-name-memory"}}

        # Introduce ourselves
        graph.invoke({
            "messages": ["Hi! My name is Alex"],
            "context": {},
            "current_step": "start"
        }, config)

        # Ask for name
        result = graph.invoke({
            "messages": ["What is my name?"],
            "context": {},
            "current_step": "start"
        }, config)

        messages = result.get("messages", [])
        last_response = messages[-1].lower() if messages else ""

        if "alex" in last_response:
            results["passed"].append("remembers_user_name")
        else:
            results["failed"].append(
                f"remembers_user_name: expected 'alex' in response, "
                f"got: '{messages[-1] if messages else 'no messages'}'"
            )
    except Exception as e:
        results["failed"].append(f"remembers_user_name: {e}")

    # Test 5: Thread isolation - different users have separate state
    try:
        graph = agent.graph
        config_a = {"configurable": {"thread_id": "user-alice"}}
        config_b = {"configurable": {"thread_id": "user-bob"}}

        # Alice's conversation
        graph.invoke({
            "messages": ["My name is Alice"],
            "context": {},
            "current_step": "start"
        }, config_a)
        graph.invoke({
            "messages": ["More from Alice"],
            "context": {},
            "current_step": "start"
        }, config_a)
        result_a = graph.invoke({
            "messages": ["Alice again"],
            "context": {},
            "current_step": "start"
        }, config_a)

        # Bob's conversation (separate)
        result_b = graph.invoke({
            "messages": ["My name is Bob"],
            "context": {},
            "current_step": "start"
        }, config_b)

        alice_msgs = len(result_a.get("messages", []))
        bob_msgs = len(result_b.get("messages", []))

        if bob_msgs < alice_msgs:
            results["passed"].append("thread_isolation")
        else:
            results["failed"].append(
                f"thread_isolation: threads not isolated "
                f"(Alice: {alice_msgs}, Bob: {bob_msgs})"
            )
    except Exception as e:
        results["failed"].append(f"thread_isolation: {e}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_persistence.py <path_to_agent.py>")
        sys.exit(1)

    agent_path = sys.argv[1]
    results = run_tests(agent_path)

    print(json.dumps(results, indent=2))

    if results["error"] or results["failed"]:
        sys.exit(1)
    sys.exit(0)
