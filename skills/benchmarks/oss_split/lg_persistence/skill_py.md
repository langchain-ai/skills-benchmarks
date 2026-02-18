---
name: LangGraph Persistence (Python)
description: "[LangGraph] Implementing persistence and checkpointing in LangGraph: saving state, resuming execution, thread IDs, and checkpointer libraries"
---

<overview>
LangGraph's persistence layer enables durable execution by checkpointing graph state at every super-step. This unlocks human-in-the-loop, memory, time travel, and fault-tolerance capabilities.

**Key Components:**
- **Checkpointer**: Saves/loads graph state
- **Thread ID**: Identifier for checkpoint sequences
- **Checkpoints**: Snapshots of state at each step
</overview>

<checkpointer-selection>
| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `InMemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Partial Single-user |
| `PostgresSaver` | Production | PostgreSQL | Yes |
| `AsyncPostgresSaver` | Async production | PostgreSQL | Yes |
</checkpointer-selection>

<ex-basic-persistence>
```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def add_message(state: State) -> dict:
    return {"messages": ["Bot response"]}

# Create checkpointer
checkpointer = InMemorySaver()

# Compile with checkpointer
graph = (
    StateGraph(State)
    .add_node("respond", add_message)
    .add_edge(START, "respond")
    .add_edge("respond", END)
    .compile(checkpointer=checkpointer)  # Enable persistence
)

# First invocation with thread_id
config = {"configurable": {"thread_id": "conversation-1"}}
result1 = graph.invoke({"messages": ["Hello"]}, config)
print(len(result1["messages"]))  # 2

# Second invocation - state persisted
result2 = graph.invoke({"messages": ["How are you?"]}, config)
print(len(result2["messages"]))  # 4 (previous + new)
```
</ex-basic-persistence>

<ex-sqlite-persistence>
```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create SQLite checkpointer
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

graph = (
    StateGraph(State)
    .add_node("process", process_node)
    .add_edge(START, "process")
    .add_edge("process", END)
    .compile(checkpointer=checkpointer)
)

# Use with thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"data": "test"}, config)
```
</ex-sqlite-persistence>

<ex-async-postgres-persistence>
```python
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def main():
    # Create async Postgres checkpointer
    async with AsyncPostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/db"
    ) as checkpointer:
        graph = (
            StateGraph(State)
            .add_node("process", process_node)
            .add_edge(START, "process")
            .add_edge("process", END)
            .compile(checkpointer=checkpointer)
        )

        config = {"configurable": {"thread_id": "thread-1"}}
        result = await graph.ainvoke({"data": "test"}, config)
```
</ex-async-postgres-persistence>

<ex-retrieving-state>
```python
# Get current state
config = {"configurable": {"thread_id": "conversation-1"}}
current_state = graph.get_state(config)
print(current_state.values)  # Current state
print(current_state.next)    # Next nodes to execute

# Get state history
for state in graph.get_state_history(config):
    print(f"Step: {state.values}")
```
</ex-retrieving-state>

<ex-resuming-from-checkpoint>
```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

def step1(state):
    return {"data": "step1"}

def step2(state):
    return {"data": state["data"] + "_step2"}

graph = (
    StateGraph(State)
    .add_node("step1", step1)
    .add_node("step2", step2)
    .add_edge(START, "step1")
    .add_edge("step1", "step2")
    .add_edge("step2", END)
    .compile(
        checkpointer=checkpointer,
        interrupt_before=["step2"]  # Pause before step2
    )
)

config = {"configurable": {"thread_id": "1"}}

# Run until breakpoint
result = graph.invoke({"data": "start"}, config)

# Resume execution
result = graph.invoke(None, config)  # None continues from checkpoint
```
</ex-resuming-from-checkpoint>

<ex-update-state>
```python
# Modify state before resuming
config = {"configurable": {"thread_id": "1"}}

# Update state
graph.update_state(
    config,
    {"data": "manually_updated"}
)

# Resume with updated state
result = graph.invoke(None, config)
```
</ex-update-state>

<ex-thread-management>
```python
# Different threads maintain separate state
thread1_config = {"configurable": {"thread_id": "user-alice"}}
thread2_config = {"configurable": {"thread_id": "user-bob"}}

# Alice's conversation
graph.invoke({"messages": ["Hi from Alice"]}, thread1_config)

# Bob's conversation (separate state)
graph.invoke({"messages": ["Hi from Bob"]}, thread2_config)

# Alice's state is isolated from Bob's
```
</ex-thread-management>

<ex-checkpointer-in-subgraphs>
```python
from langgraph.graph import StateGraph, START

# Only parent graph needs checkpointer
def subgraph_node(state):
    return {"data": "subgraph"}

subgraph = (
    StateGraph(State)
    .add_node("process", subgraph_node)
    .add_edge(START, "process")
    .compile()  # No checkpointer needed
)

# Parent graph with checkpointer
checkpointer = InMemorySaver()

parent = (
    StateGraph(State)
    .add_node("subgraph", subgraph)
    .add_edge(START, "subgraph")
    .compile(checkpointer=checkpointer)  # Propagates to subgraph
)
```
</ex-checkpointer-in-subgraphs>

<boundaries>
### What You CAN Configure

- Choose checkpointer implementation
- Specify thread IDs
- Retrieve state at any checkpoint
- Update state between invocations
- Set breakpoints for pausing
- Access state history
- Resume from any checkpoint

### What You CANNOT Configure

- Checkpoint format/schema (internal)
- Checkpoint timing (every super-step)
- Thread ID structure (arbitrary strings only)
</boundaries>

<fix-thread-id-required>
```python
# WRONG: WRONG - No thread_id, state not saved
graph.invoke({"data": "test"})  # Lost after execution!

# CORRECT: CORRECT - Always provide thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```
</fix-thread-id-required>

<fix-inmemory-not-for-production>
```python
# WRONG: WRONG - Data lost on restart
checkpointer = InMemorySaver()  # In-memory only!

# CORRECT: CORRECT - Use persistent storage
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
```
</fix-inmemory-not-for-production>

<fix-resume-with-none>
```python
# WRONG: WRONG - Providing input restarts
graph.invoke({"new": "data"}, config)  # Restarts from beginning

# CORRECT: CORRECT - Use None to resume
graph.invoke(None, config)  # Resumes from checkpoint
```
</fix-resume-with-none>

<fix-update-state-reducers>
```python
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]

# Assume current state: {"items": ["A", "B"]}

# update_state passes through reducers
graph.update_state(config, {"items": ["C"]})
# Result: {"items": ["A", "B", "C"]}  # Appended!

# To overwrite, use different approach
from langgraph.types import Overwrite
graph.update_state(config, {"items": Overwrite(["C"])})
# Result: {"items": ["C"]}  # Replaced
```
</fix-update-state-reducers>

<fix-checkpointer-at-compile>
```python
# WRONG: WRONG - Checkpointer after compile
graph = builder.compile()
graph.checkpointer = checkpointer  # Too late!

# CORRECT: CORRECT - Pass during compile
graph = builder.compile(checkpointer=checkpointer)
```
</fix-checkpointer-at-compile>

<links>
- [Persistence Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/python/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/python/langgraph/persistence#threads)
- [Time Travel](https://docs.langchain.com/langsmith/human-in-the-loop-time-travel)
</links>
