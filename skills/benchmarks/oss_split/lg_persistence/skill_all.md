---
name: LangGraph Persistence
description: "[LangGraph] Implementing persistence and checkpointing in LangGraph: saving state, resuming execution, thread IDs, and checkpointer libraries"
---


## Overview

LangGraph's persistence layer enables durable execution by checkpointing graph state at every super-step. This unlocks human-in-the-loop, memory, time travel, and fault-tolerance capabilities.

**Key Components:**
- **Checkpointer**: Saves/loads graph state
- **Thread ID**: Identifier for checkpoint sequences
- **Checkpoints**: Snapshots of state at each step

## Decision Table: Checkpointer Selection

| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `InMemorySaver` / `MemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Single-user only |
| `PostgresSaver` | Production | PostgreSQL | Yes |
| `AsyncPostgresSaver` (Python) | Async production | PostgreSQL | Yes |

## Code Examples

### Basic Persistence with InMemorySaver / MemorySaver

#### Python
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

#### TypeScript
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

### SQLite Persistence

#### Python
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

#### TypeScript
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

### PostgreSQL Persistence

#### Python
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

#### TypeScript
```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

// Create Postgres checkpointer
const checkpointer = await PostgresSaver.fromConnString(
  "postgresql://user:pass@localhost/db"
);

const graph = new StateGraph(State)
  .addNode("process", processNode)
  .addEdge(START, "process")
  .addEdge("process", END)
  .compile({ checkpointer });

const config = { configurable: { thread_id: "thread-1" } };
const result = await graph.invoke({ data: "test" }, config);
```

### Retrieving State

#### Python
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

#### TypeScript
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

### Resuming from Checkpoint

#### Python
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

#### TypeScript
```typescript
import { MemorySaver, StateGraph, START, END } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const step1 = async (state) => ({ data: "step1" });
const step2 = async (state) => ({ data: state.data + "_step2" });

const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", END)
  .compile({
    checkpointer,
    interruptBefore: ["step2"],  // Pause before step2
  });

const config = { configurable: { thread_id: "1" } };

// Run until breakpoint
await graph.invoke({ data: "start" }, config);

// Resume execution
await graph.invoke(null, config);  // null continues from checkpoint
```

### Update State

#### Python
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

#### TypeScript
```typescript
// Modify state before resuming
const config = { configurable: { thread_id: "1" } };

// Update state
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
await graph.invoke(null, config);
```

### Thread Management

#### Python
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

#### TypeScript
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

### Checkpointer in Subgraphs

#### Python
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

#### TypeScript
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

## Boundaries

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

## Gotchas

### 1. Thread ID Required for Persistence

#### Python
```python
# WRONG - No thread_id, state not saved
graph.invoke({"data": "test"})  # Lost after execution!

# CORRECT - Always provide thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```

#### TypeScript
```typescript
// WRONG - No thread_id, state not saved
await graph.invoke({ data: "test" });  // Lost after execution!

// CORRECT - Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```

### 2. InMemorySaver / MemorySaver Not for Production

#### Python
```python
# WRONG - Data lost on restart
checkpointer = InMemorySaver()  # In-memory only!

# CORRECT - Use persistent storage
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
```

#### TypeScript
```typescript
// WRONG - Data lost on restart
const checkpointer = new MemorySaver();  // In-memory only!

// CORRECT - Use persistent storage
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = await PostgresSaver.fromConnString("postgresql://...");
```

### 3. Resuming Requires None/null Input

#### Python
```python
# WRONG - Providing input restarts
graph.invoke({"new": "data"}, config)  # Restarts from beginning

# CORRECT - Use None to resume
graph.invoke(None, config)  # Resumes from checkpoint
```

#### TypeScript
```typescript
// WRONG - Providing input restarts
await graph.invoke({ new: "data" }, config);  // Restarts from beginning

// CORRECT - Use null to resume
await graph.invoke(null, config);  // Resumes from checkpoint
```

### 4. Update State Respects Reducers (Python)

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

### 5. Checkpointer Must Be Passed to Compile

#### Python
```python
# WRONG - Checkpointer after compile
graph = builder.compile()
graph.checkpointer = checkpointer  # Too late!

# CORRECT - Pass during compile
graph = builder.compile(checkpointer=checkpointer)
```

#### TypeScript
```typescript
// WRONG - Checkpointer after compile
const graph = builder.compile();
graph.checkpointer = checkpointer;  // Too late!

// CORRECT - Pass during compile
const graph = builder.compile({ checkpointer });
```

### 6. Always Await Async Operations (TypeScript)

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" }, config);
console.log(result.values);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" }, config);
console.log(result.values);  // Works!
```

## Links

### Python
- [Persistence Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/python/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/python/langgraph/persistence#threads)
- [Time Travel](https://docs.langchain.com/langsmith/human-in-the-loop-time-travel)

### TypeScript
- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/javascript/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/javascript/langgraph/persistence#threads)
