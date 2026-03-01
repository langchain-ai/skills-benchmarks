"""Execution-based tests for LangGraph persistence and state fixes.

The broken code has multiple issues:
1. No checkpointer - state not saved between invocations
2. No thread_id usage - conversations not isolated
3. Missing reducer on messages list - messages get overwritten, not accumulated
4. Node returns entire state instead of partial update dict

These tests verify the code actually works, not just that it contains patterns.
"""

from scaffold.python.validation.runner import TestRunner


def _require_graph(runner):
    """Load and return graph from artifact. Cached by runner.load_module()."""
    module = runner.load_module(runner.artifacts[0])
    if module is None:
        return None
    return module.graph


# =============================================================================
# Checks — each must call runner.passed() or runner.failed()
# =============================================================================


def check_has_checkpointer(runner):
    """Graph has a checkpointer configured."""
    graph = _require_graph(runner)
    if graph is None:
        return
    if hasattr(graph, "checkpointer") and graph.checkpointer is not None:
        runner.passed("has_checkpointer")
    else:
        runner.failed(
            "has_checkpointer: graph.checkpointer is None - need to add checkpointer to compile()"
        )


def check_state_persists(runner):
    """State persists across invocations with thread_id."""
    graph = _require_graph(runner)
    if graph is None:
        return
    try:
        config = {"configurable": {"thread_id": "test-persistence"}}
        result1 = graph.invoke(
            {"messages": ["Hello"], "context": {}, "current_step": "start"}, config
        )
        msgs_after_1 = len(result1.get("messages", []))
        result2 = graph.invoke(
            {"messages": ["How are you?"], "context": {}, "current_step": "start"}, config
        )
        msgs_after_2 = len(result2.get("messages", []))
        if msgs_after_2 > msgs_after_1:
            runner.passed("state_persists_across_calls")
        else:
            runner.failed(
                f"state_persists_across_calls: messages didn't accumulate "
                f"(call 1: {msgs_after_1}, call 2: {msgs_after_2}) - "
                "need checkpointer + thread_id"
            )
    except Exception as e:
        runner.failed(f"state_persists_across_calls: {e}")


def check_messages_accumulate(runner):
    """Messages accumulate within single invocation (reducer works)."""
    graph = _require_graph(runner)
    if graph is None:
        return
    try:
        config = {"configurable": {"thread_id": "test-reducer"}}
        result = graph.invoke(
            {"messages": ["Test message"], "context": {}, "current_step": "start"}, config
        )
        messages = result.get("messages", [])
        if len(messages) >= 2:
            runner.passed("messages_accumulate_with_reducer")
        else:
            runner.failed(
                f"messages_accumulate_with_reducer: expected >=2 messages, got {len(messages)} - "
                "need Annotated[list, operator.add] reducer"
            )
    except Exception as e:
        runner.failed(f"messages_accumulate_with_reducer: {e}")


def check_no_duplication(runner):
    """Nodes return partial updates, not entire state."""
    graph = _require_graph(runner)
    if graph is None:
        return
    try:
        config = {"configurable": {"thread_id": "test-no-duplication"}}
        result = graph.invoke(
            {"messages": ["Hello there"], "context": {}, "current_step": "start"}, config
        )
        messages = result.get("messages", [])
        input_count = sum(1 for m in messages if m == "Hello there")
        if input_count == 1 and len(messages) == 2:
            runner.passed("no_message_duplication")
        elif input_count > 1:
            runner.failed(
                f"no_message_duplication: input message duplicated {input_count} times - "
                "node is returning entire state instead of partial update dict"
            )
        else:
            runner.failed(
                f"no_message_duplication: unexpected message count {len(messages)}, "
                f"messages: {messages}"
            )
    except Exception as e:
        runner.failed(f"no_message_duplication: {e}")


def check_remembers_name(runner):
    """Bot remembers user's name across turns."""
    graph = _require_graph(runner)
    if graph is None:
        return
    try:
        config = {"configurable": {"thread_id": "test-name-memory"}}
        graph.invoke(
            {"messages": ["Hi! My name is Alex"], "context": {}, "current_step": "start"}, config
        )
        result = graph.invoke(
            {"messages": ["What is my name?"], "context": {}, "current_step": "start"}, config
        )
        messages = result.get("messages", [])
        last_response = messages[-1].lower() if messages else ""
        if "alex" in last_response:
            runner.passed("remembers_user_name")
        else:
            runner.failed(
                f"remembers_user_name: expected 'alex' in response, got: "
                f"'{messages[-1] if messages else 'no messages'}'"
            )
    except Exception as e:
        runner.failed(f"remembers_user_name: {e}")


def check_thread_isolation(runner):
    """Different thread_ids have separate state."""
    graph = _require_graph(runner)
    if graph is None:
        return
    try:
        config_a = {"configurable": {"thread_id": "user-alice"}}
        config_b = {"configurable": {"thread_id": "user-bob"}}
        graph.invoke(
            {"messages": ["My name is Alice"], "context": {}, "current_step": "start"}, config_a
        )
        graph.invoke(
            {"messages": ["More from Alice"], "context": {}, "current_step": "start"}, config_a
        )
        result_a = graph.invoke(
            {"messages": ["Alice again"], "context": {}, "current_step": "start"}, config_a
        )
        result_b = graph.invoke(
            {"messages": ["My name is Bob"], "context": {}, "current_step": "start"}, config_b
        )
        alice_msgs = len(result_a.get("messages", []))
        bob_msgs = len(result_b.get("messages", []))
        if bob_msgs < alice_msgs:
            runner.passed("thread_isolation")
        else:
            runner.failed(
                f"thread_isolation: threads not isolated (Alice: {alice_msgs}, Bob: {bob_msgs})"
            )
    except Exception as e:
        runner.failed(f"thread_isolation: {e}")


if __name__ == "__main__":
    TestRunner.run(
        [
            check_has_checkpointer,
            check_state_persists,
            check_messages_accumulate,
            check_no_duplication,
            check_remembers_name,
            check_thread_isolation,
        ]
    )
