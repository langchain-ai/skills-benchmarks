---
name: LangGraph Interrupts (Python)
description: "[LangGraph] Human-in-the-loop with dynamic interrupts and breakpoints: pausing execution for human review and resuming with Command"
---

<overview>
Interrupts enable human-in-the-loop patterns by pausing graph execution for external input. LangGraph saves state and waits indefinitely until you resume execution.

**Key Types:**
- **Dynamic Interrupts**: `interrupt()` function called in nodes
- **Static Breakpoints**: `interrupt_before`/`interrupt_after` at compile time
</overview>

<interrupt-type-selection>
| Type | When Set | Use Case |
|------|----------|----------|
| Dynamic (`interrupt()`) | Inside node code | Conditional pausing based on logic |
| Static (`interrupt_before`) | At compile time | Debug/test before specific nodes |
| Static (`interrupt_after`) | At compile time | Review output after specific nodes |
</interrupt-type-selection>

<ex-dynamic-interrupt>
```python
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

def review_node(state):
    # Conditionally pause for review
    if state["needs_review"]:
        # Pause and surface data to user
        user_response = interrupt({
            "action": "review",
            "data": state["draft"],
            "question": "Approve this draft?"
        })

        # user_response comes from Command(resume=...)
        if user_response == "reject":
            return {"status": "rejected"}

    return {"status": "approved"}

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("review", review_node)
    .add_edge(START, "review")
    .add_edge("review", END)
    .compile(checkpointer=checkpointer)  # Required!
)

# Initial invocation - will pause
config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"needs_review": True, "draft": "content"}, config)

# Check for interrupt
if "__interrupt__" in result:
    print(result["__interrupt__"])  # See interrupt payload

# Resume with user decision
from langgraph.types import Command
result = graph.invoke(
    Command(resume="approve"),  # User's response
    config
)
```
</ex-dynamic-interrupt>

<ex-static-breakpoints>
```python
checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_node("step3", step3)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", "step3")
    .add_edge("step3", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"],  # Pause before step2
        interrupt_after=["step3"]    # Pause after step3
    )
)

config = {"configurable": {"thread_id": "1"}}

# Run until first breakpoint
graph.invoke({"data": "test"}, config)

# Resume (pauses at next breakpoint)
graph.invoke(None, config)  # None = resume

# Resume again
graph.invoke(None, config)
```
</ex-static-breakpoints>

<ex-tool-review-pattern>
```python
from langgraph.types import interrupt, Command

def tool_executor(state):
    tool_calls = state["messages"][-1].tool_calls

    for tool_call in tool_calls:
        # Pause for each tool call
        user_decision = interrupt({
            "tool": tool_call["name"],
            "args": tool_call["args"],
            "question": "Execute this tool?"
        })

        if user_decision["type"] == "approve":
            # Execute tool
            result = execute_tool(tool_call)
        elif user_decision["type"] == "edit":
            # Use edited args
            result = execute_tool(user_decision["args"])
        else:  # reject
            result = "Tool execution rejected"

        # Store result
        results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    return {"messages": results}

# Usage
result = graph.invoke({"messages": [...]}, config)

# Review and approve
graph.invoke(Command(resume={"type": "approve"}), config)

# Or edit args
graph.invoke(
    Command(resume={"type": "edit", "args": {"query": "modified"}}),
    config
)

# Or reject
graph.invoke(Command(resume={"type": "reject"}), config)
```
</ex-tool-review-pattern>

<ex-editing-state-during-interrupt>
```python
config = {"configurable": {"thread_id": "1"}}

# Run until interrupt
graph.invoke({"data": "test"}, config)

# Modify state before resuming
graph.update_state(config, {"data": "manually edited"})

# Resume with edited state
graph.invoke(None, config)
```
</ex-editing-state-during-interrupt>

<ex-stream-with-interrupts>
```python
async for mode, chunk in graph.astream(
    {"query": "test"},
    stream_mode=["updates", "messages"],
    config={"configurable": {"thread_id": "1"}}
):
    if mode == "updates":
        if "__interrupt__" in chunk:
            # Handle interrupt
            interrupt_info = chunk["__interrupt__"][0].value
            user_input = get_user_input(interrupt_info)

            # Resume
            initial_input = Command(resume=user_input)
            break
```
</ex-stream-with-interrupts>

<boundaries>
### What You CAN Configure

- Call `interrupt()` anywhere in nodes
- Set compile-time breakpoints
- Resume with `Command(resume=...)`
- Edit state during interrupts
- Stream while handling interrupts
- Conditional interrupt logic

### What You CANNOT Configure

- Interrupt without checkpointer
- Modify interrupt mechanism
- Resume without thread_id
</boundaries>

<fix-checkpointer-required>
```python
# WRONG: WRONG - No checkpointer
graph = builder.compile()  # No persistence!
graph.invoke(...)  # Interrupt won't work

# CORRECT: CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
</fix-checkpointer-required>

<fix-thread-id-required>
```python
# WRONG: WRONG - No thread_id
graph.invoke({"data": "test"})  # Can't resume!

# CORRECT: CORRECT
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```
</fix-thread-id-required>

<fix-resume-with-command>
```python
# WRONG: WRONG - Passing regular dict
graph.invoke({"resume_data": "approve"}, config)  # Restarts!

# CORRECT: CORRECT - Use Command
from langgraph.types import Command
graph.invoke(Command(resume="approve"), config)
```
</fix-resume-with-command>

<fix-dynamic-over-static-breakpoints>
```python
# WRONG: ANTI-PATTERN - Static breakpoints for all users
compile(interrupt_before=["action"])  # Pauses for everyone!

# CORRECT: BETTER - Dynamic interrupts with logic
def node(state):
    if state["requires_approval"]:  # Conditional
        interrupt({"action": "approve?"})
```
</fix-dynamic-over-static-breakpoints>

<links>
- [Interrupts Guide](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Command API](https://docs.langchain.com/oss/python/langgraph/use-graph-api#combine-control-flow-and-state-updates-with-command)
</links>
