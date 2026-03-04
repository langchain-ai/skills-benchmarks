---
name: langgraph-persistence-js
description: "[LangGraph] Implementing persistence and checkpointing in LangGraph: saving state, resuming execution, thread IDs, and checkpointer libraries"
---

<overview>
LangGraph's persistence layer enables durable execution by checkpointing graph state at every super-step. This unlocks human-in-the-loop, memory, time travel, and fault-tolerance capabilities.

Key Components:
- **Checkpointer**: Saves/loads graph state
- **Thread ID**: Identifier for checkpoint sequences
- **Checkpoints**: Snapshots of state at each step
</overview>

<checkpointer-selection>

| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `MemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Partial Single-user |
| `PostgresSaver` | Production | PostgreSQL | Yes |

</checkpointer-selection>

<ex-memory-saver>
Basic persistence with MemorySaver:

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
</ex-memory-saver>

<ex-sqlite>
SQLite persistence for local development:

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
</ex-sqlite>

<ex-postgres>
PostgreSQL persistence for production:

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
</ex-postgres>

<ex-get-state>
Retrieve current state and history:

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
</ex-get-state>

<ex-resume-from-checkpoint>
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
</ex-resume-from-checkpoint>

<ex-update-state>
Modify state before resuming:

```typescript
// Modify state before resuming
const config = { configurable: { thread_id: "1" } };

// Update state
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
await graph.invoke(null, config);
```
</ex-update-state>

<ex-threads>
Manage separate conversations with thread IDs:

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
</ex-threads>

<ex-subgraphs>
Checkpointer propagates to subgraphs:

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
</ex-subgraphs>

<boundaries>
What You CAN Configure:
- Choose checkpointer implementation
- Specify thread IDs
- Retrieve state at any checkpoint
- Update state between invocations
- Set breakpoints for pausing
- Access state history
- Resume from any checkpoint

What You CANNOT Configure:
- Checkpoint format/schema (internal)
- Checkpoint timing (every super-step)
- Thread ID structure (arbitrary strings only)
</boundaries>

<fix-thread-id>
Always provide thread_id for persistence:

```typescript
// WRONG - No thread_id, state not saved
await graph.invoke({ data: "test" });  // Lost after execution!

// CORRECT - Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```
</fix-thread-id>

<fix-memory-production>
Use persistent storage for production:

```typescript
// WRONG - Data lost on restart
const checkpointer = new MemorySaver();  // In-memory only!

// CORRECT - Use persistent storage
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = PostgresSaver.fromConnString("postgresql://...");
await checkpointer.setup(); // only needed on first use to create tables
```
</fix-memory-production>

<fix-resume-null>
Use null input to resume from checkpoint:

```typescript
// WRONG - Providing input restarts
await graph.invoke({ new: "data" }, config);  // Restarts from beginning

// CORRECT - Use null to resume
await graph.invoke(null, config);  // Resumes from checkpoint
```
</fix-resume-null>

<fix-await>
Always await async operations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" }, config);
console.log(result.values);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" }, config);
console.log(result.values);  // Works!
```
</fix-await>

<documentation-links>
- [Persistence Guide](https://docs.langchain.com/oss/javascript/langgraph/persistence)
- [Checkpointer Libraries](https://docs.langchain.com/oss/javascript/langgraph/persistence#checkpointer-libraries)
- [Thread Management](https://docs.langchain.com/oss/javascript/langgraph/persistence#threads)
</documentation-links>
