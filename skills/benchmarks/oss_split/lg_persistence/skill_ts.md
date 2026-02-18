---
name: LangGraph Persistence (TypeScript)
description: "[LangGraph] Implementing persistence and checkpointing in LangGraph: saving state, resuming execution, thread IDs, and checkpointer libraries"
---

# langgraph-persistence (JavaScript/TypeScript)


## Overview

LangGraph's persistence layer enables durable execution by checkpointing graph state at every super-step. This unlocks human-in-the-loop, memory, time travel, and fault-tolerance capabilities.

**Key Components:**
- **Checkpointer**: Saves/loads graph state
- **Thread ID**: Identifier for checkpoint sequences
- **Checkpoints**: Snapshots of state at each step

## Decision Table: Checkpointer Selection

| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `MemorySaver` | Testing, development | In-memory only | ❌ No |
| `SqliteSaver` | Local development | SQLite file | ⚠️ Single-user |
| `PostgresSaver` | Production | PostgreSQL | ✅ Yes |

## Code Examples

### Basic Persistence with MemorySaver

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

```typescript
// Modify state before resuming
const config = { configurable: { thread_id: "1" } };

// Update state
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
await graph.invoke(null, config);
```

### Thread Management

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

✅ Choose checkpointer implementation
✅ Specify thread IDs
✅ Retrieve state at any checkpoint
✅ Update state between invocations
✅ Set breakpoints for pausing
✅ Access state history
✅ Resume from any checkpoint

### What You CANNOT Configure

❌ Checkpoint format/schema (internal)
❌ Checkpoint timing (every super-step)
❌ Thread ID structure (arbitrary strings only)

## Gotchas

### 1. Thread ID Required for Persistence

```typescript
// ❌ WRONG - No thread_id, state not saved
await graph.invoke({ data: "test" });  // Lost after execution!

// ✅ CORRECT - Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```

### 2. MemorySaver Not for Production

```typescript
// ❌ WRONG - Data lost on restart
const checkpointer = new MemorySaver();  // In-memory only!

// ✅ CORRECT - Use persistent storage
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = await PostgresSaver.fromConnString("postgresql://...");
```

### 3. Resuming Requires null Input

```typescript
// ❌ WRONG - Providing input restarts
await graph.invoke({ new: "data" }, config);  // Restarts from beginning

// ✅ CORRECT - Use null to resume
await graph.invoke(null, config);  // Resumes from checkpoint
```

### 4. Always Await Async Operations

```typescript
// ❌ WRONG - Forgetting await
const result = graph.invoke({ data: "test" }, config);
console.log(result.values);  // undefined!

// ✅ CORRECT
const result = await graph.invoke({ data: "test" }, config);
console.log(result.values);  // Works!
```

### 5. Checkpointer Must Be Passed to Compile

```typescript
// ❌ WRONG - Checkpointer after compile
const graph = builder.compile();
graph.checkpointer = checkpointer;  // Too late!

// ✅ CORRECT - Pass during compile
const graph = builder.compile({ checkpointer });
```

## Links

- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/javascript/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/javascript/langgraph/persistence#threads)
