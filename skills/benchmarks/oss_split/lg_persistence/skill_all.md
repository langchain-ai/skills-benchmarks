---
name: LangGraph Persistence
description: "[LangGraph] Implementing persistence and checkpointing in LangGraph: saving state, resuming execution, thread IDs, and checkpointer libraries"
---

<overview>
LangGraph's persistence layer enables durable execution by checkpointing graph state at every super-step. This unlocks human-in-the-loop, memory, time travel, and fault-tolerance capabilities.

**Key Components:**
- **Checkpointer**: Saves/loads graph state
- **Thread ID**: Identifier for checkpoint sequences
- **Checkpoints**: Snapshots of state at each step
</overview>

<decision-table>

| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `InMemorySaver` / `MemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Single-user only |
| `PostgresSaver` | Production | PostgreSQL | Yes |
| `AsyncPostgresSaver` (Python) | Async production | PostgreSQL | Yes |

</decision-table>

<ex-basic>
<python>
In-memory checkpointer for development:

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
</python>

<typescript>
In-memory checkpointer for development:

```typescript
import { MemorySaver, StateGraph, StateSchema, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  messages: z.array(z.string()),
});

const addMessage = async (state: typeof State.State) => {
  return { messages: [...state.messages, "Bot response"] };
};

// Create checkpointer
const checkpointer = new MemorySaver();

// Compile with checkpointer
const graph = new StateGraph(State)
  .addNode("respond", addMessage)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });  // Enable persistence

// First invocation with thread_id
const config = { configurable: { thread_id: "conversation-1" } };
const result1 = await graph.invoke({ messages: ["Hello"] }, config);
console.log(result1.messages.length);  // 2

// Second invocation - state persisted
const result2 = await graph.invoke({ messages: ["How are you?"] }, config);
console.log(result2.messages.length);  // 4 (previous + new)
```
</typescript>
</ex-basic>

<ex-sqlite>
<python>
File-based persistence for local development:

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
</python>

<typescript>
File-based persistence for local development:

```typescript
import { SqliteSaver } from "@langchain/langgraph-checkpoint-sqlite";

// Create SQLite checkpointer
const checkpointer = SqliteSaver.fromConnString("checkpoints.db");

const graph = new StateGraph(State)
  .addNode("process", processNode)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile({ checkpointer });

// Use with thread_id
const config = { configurable: { thread_id: "user-123" } };
const result = await graph.invoke({ data: "test" }, config);
```
</typescript>
</ex-sqlite>

<ex-postgres>
<python>
Production-ready async persistence:

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
</python>

<typescript>
Production-ready persistence:

```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

// Create Postgres checkpointer
const checkpointer = PostgresSaver.fromConnString(
  "postgresql://user:pass@localhost/db"
);
await checkpointer.setup(); // only needed on first use to create tables

const graph = new StateGraph(State)
  .addNode("process", processNode)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "thread-1" } };
const result = await graph.invoke({ data: "test" }, config);
```
</typescript>
</ex-postgres>

<ex-get-state>
<python>
Get current state and history:

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
</python>

<typescript>
Get current state and history:

```typescript
// Get current state
const config = { configurable: { thread_id: "conversation-1" } };
const currentState = await graph.getState(config);
console.log(currentState.values);  // Current state
console.log(currentState.next);    // Next nodes to execute

// Get state history
const history = await graph.getStateHistory(config);
for await (const state of history) {
  console.log("Step:", state.values);
}
```
</typescript>
</ex-get-state>

<ex-resume-from-checkpoint>
<python>
Time travel: browse checkpoint history and replay or fork from a past state.
```python
config = {"configurable": {"thread_id": "session-1"}}

result = graph.invoke({"messages": ["start"]}, config)

# Browse checkpoint history
states = list(graph.get_state_history(config))

# Replay from a past checkpoint
past = states[-2]
result = graph.invoke(None, past.config)  # None = resume from checkpoint

# Or fork: update state at a past checkpoint, then resume
fork_config = graph.update_state(past.config, {"messages": ["edited"]})
result = graph.invoke(None, fork_config)
```
</python>

<typescript>
Time travel: browse checkpoint history and replay or fork from a past state.
```typescript
const config = { configurable: { thread_id: "session-1" } };

const result = await graph.invoke({ messages: ["start"] }, config);

// Browse checkpoint history (async iterable, collect to array)
const states: Awaited<ReturnType<typeof graph.getState>>[] = [];
for await (const state of graph.getStateHistory(config)) {
  states.push(state);
}

// Replay from a past checkpoint
const past = states[states.length - 2];
const replayed = await graph.invoke(null, past.config);  // null = resume from checkpoint

// Or fork: update state at a past checkpoint, then resume
const forkConfig = await graph.updateState(past.config, { messages: ["edited"] });
const forked = await graph.invoke(null, forkConfig);
```
</typescript>
</ex-resume-from-checkpoint>

<ex-update-state>
<python>
Modify state before resuming:

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
</python>

<typescript>
Modify state before resuming:

```typescript
// Modify state before resuming
const config = { configurable: { thread_id: "1" } };

// Update state
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
await graph.invoke(null, config);
```
</typescript>
</ex-update-state>

<ex-threads>
<python>
Isolated state per thread:

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
</python>

<typescript>
Isolated state per thread:

```typescript
// Different threads maintain separate state
const thread1Config = { configurable: { thread_id: "user-alice" } };
const thread2Config = { configurable: { thread_id: "user-bob" } };

// Alice's conversation
await graph.invoke({ messages: ["Hi from Alice"] }, thread1Config);

// Bob's conversation (separate state)
await graph.invoke({ messages: ["Hi from Bob"] }, thread2Config);

// Alice's state is isolated from Bob's
```
</typescript>
</ex-threads>

<ex-subgraphs>
<python>
Parent checkpointer propagates to subgraphs:

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
</python>

<typescript>
Parent checkpointer propagates to subgraphs:

```typescript
import { MemorySaver, StateGraph, START } from "@langchain/langgraph";

// Only parent graph needs checkpointer
const subgraphNode = async (state) => ({ data: "subgraph" });

const subgraph = new StateGraph(State)
  .addNode("process", subgraphNode)
  .addEdge(START, "process")
  .compile();  // No checkpointer needed

// Parent graph with checkpointer
const checkpointer = new MemorySaver();

const parent = new StateGraph(State)
  .addNode("subgraph", subgraph)
  .addEdge(START, "subgraph")
  .compile({ checkpointer });  // Propagates to subgraph
```
</typescript>
</ex-subgraphs>

<boundaries>
**What You CAN Configure**

- Choose checkpointer implementation
- Specify thread IDs
- Retrieve state at any checkpoint
- Update state between invocations
- Set breakpoints for pausing
- Access state history
- Resume from any checkpoint

**What You CANNOT Configure**

- Checkpoint format/schema (internal)
- Checkpoint timing (every super-step)
- Thread ID structure (arbitrary strings only)
</boundaries>

<fix-thread-id-required>
<python>
Provide thread_id for persistence:

```python
# WRONG - No thread_id, state not saved
graph.invoke({"data": "test"})  # Lost after execution!

# CORRECT - Always provide thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```
</python>

<typescript>
Provide thread_id for persistence:

```typescript
// WRONG - No thread_id, state not saved
await graph.invoke({ data: "test" });  // Lost after execution!

// CORRECT - Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```
</typescript>
</fix-thread-id-required>

<fix-memory-saver-not-for-production>
<python>
Use persistent storage in production:

```python
# WRONG - Data lost on restart
checkpointer = InMemorySaver()  # In-memory only!

# CORRECT - Use persistent storage
from langgraph.checkpoint.postgres import PostgresSaver
with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    graph = builder.compile(checkpointer=checkpointer)
```
</python>

<typescript>
Use persistent storage in production:

```typescript
// WRONG - Data lost on restart
const checkpointer = new MemorySaver();  // In-memory only!

// CORRECT - Use persistent storage
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = PostgresSaver.fromConnString("postgresql://...");
await checkpointer.setup(); // only needed on first use to create tables
```
</typescript>
</fix-memory-saver-not-for-production>

<fix-resume-requires-null>
<python>
Use None to resume from checkpoint:

```python
# WRONG - Providing input restarts
graph.invoke({"new": "data"}, config)  # Restarts from beginning

# CORRECT - Use None to resume
graph.invoke(None, config)  # Resumes from checkpoint
```
</python>

<typescript>
Use null to resume from checkpoint:

```typescript
// WRONG - Providing input restarts
await graph.invoke({ new: "data" }, config);  // Restarts from beginning

// CORRECT - Use null to resume
await graph.invoke(null, config);  // Resumes from checkpoint
```
</typescript>
</fix-resume-requires-null>

<fix-update-state-respects-reducers>
<python>
Updates pass through reducers:

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
</python>
</fix-update-state-respects-reducers>


<fix-await-async-operations>
<typescript>
Await all async operations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" }, config);
console.log(result.values);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" }, config);
console.log(result.values);  // Works!
```
</typescript>
</fix-await-async-operations>

<links>
**Python**
- [Persistence Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/python/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/python/langgraph/persistence#threads)
- [Time Travel](https://docs.langchain.com/langsmith/human-in-the-loop-time-travel)

**TypeScript**
- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/javascript/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/javascript/langgraph/persistence#threads)
</links>
