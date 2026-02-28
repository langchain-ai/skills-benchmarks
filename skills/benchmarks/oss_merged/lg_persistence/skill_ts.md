---
name: LangGraph Persistence & Memory (TypeScript)
description: "INVOKE THIS SKILL when your LangGraph needs to remember state across calls, use memory, or persist conversations. Covers checkpointers (MemorySaver, Postgres), thread_id configuration, and Store for long-term memory. CRITICAL: Fixes for missing thread_id, checkpointer placement, and cross-thread memory access."
---

<overview>
LangGraph's persistence layer enables durable execution by checkpointing graph state:

- **Checkpointer**: Saves/loads graph state at every super-step
- **Thread ID**: Identifies separate checkpoint sequences (conversations)
- **Store**: Cross-thread memory for user preferences, facts

**Two memory types:**
- **Short-term** (checkpointer): Thread-scoped conversation history
- **Long-term** (store): Cross-thread user preferences, facts
</overview>

<checkpointer-selection>

| Checkpointer | Use Case | Production Ready |
|--------------|----------|------------------|
| `MemorySaver` | Testing, development | No |
| `SqliteSaver` | Local development | Partial |
| `PostgresSaver` | Production | Yes |

</checkpointer-selection>

---

## Checkpointer Setup

<ex-basic-persistence>
Set up a basic graph with in-memory checkpointing and thread-based state persistence.
```typescript
import { MemorySaver, StateGraph, StateSchema, MessagesValue, START, END } from "@langchain/langgraph";
import { HumanMessage } from "@langchain/core/messages";

const State = new StateSchema({ messages: MessagesValue });

const addMessage = async (state: typeof State.State) => {
  return { messages: [{ role: "assistant", content: "Bot response" }] };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("respond", addMessage)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });

// ALWAYS provide thread_id
const config = { configurable: { thread_id: "conversation-1" } };

const result1 = await graph.invoke({ messages: [new HumanMessage("Hello")] }, config);
console.log(result1.messages.length);  // 2

const result2 = await graph.invoke({ messages: [new HumanMessage("How are you?")] }, config);
console.log(result2.messages.length);  // 4 (previous + new)
```
</ex-basic-persistence>

<ex-production-postgres>
Configure PostgreSQL-backed checkpointing for production deployments.
```typescript
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";

const checkpointer = PostgresSaver.fromConnString(
  "postgresql://user:pass@localhost/db"
);
await checkpointer.setup(); // only needed on first use to create tables

const graph = builder.compile({ checkpointer });
```
</ex-production-postgres>

---

## Thread Management

<ex-separate-threads>
Demonstrate isolated state between different thread IDs.
```typescript
// Different threads maintain separate state
const aliceConfig = { configurable: { thread_id: "user-alice" } };
const bobConfig = { configurable: { thread_id: "user-bob" } };

await graph.invoke({ messages: [new HumanMessage("Hi from Alice")] }, aliceConfig);
await graph.invoke({ messages: [new HumanMessage("Hi from Bob")] }, bobConfig);

// Alice's state is isolated from Bob's
```
</ex-separate-threads>

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
Manually update graph state before resuming execution.
```typescript
const config = { configurable: { thread_id: "session-1" } };

// Modify state before resuming
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
const result = await graph.invoke(null, config);
```
</ex-update-state>

---

## Long-Term Memory (Store)

<ex-long-term-memory-store>
Use a Store for cross-thread memory to share user preferences across conversations.
```typescript
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Save user preference
await store.put(["alice", "preferences"], "language", { preference: "short responses" });

// Node with store - access via config
const respond = async (state: typeof State.State, config: any) => {
  const item = await config.store.get(["alice", "preferences"], "language");
  return { response: `Using preference: ${item?.value?.preference}` };
};

// Compile with BOTH checkpointer and store
const graph = builder.compile({ checkpointer, store });

// Both threads access same long-term memory
const thread1 = { configurable: { thread_id: "thread-1" } };
const thread2 = { configurable: { thread_id: "thread-2" } };

await graph.invoke({ userId: "alice" }, thread1);
await graph.invoke({ userId: "alice" }, thread2);  // Same preferences!
```
</ex-long-term-memory-store>

<boundaries>
### What You CAN Configure

- Choose checkpointer implementation
- Specify thread IDs for conversation isolation
- Retrieve/update state at any checkpoint
- Use stores for cross-thread memory

### What You CANNOT Configure

- Checkpoint timing (happens every super-step)
- Share short-term memory across threads
- Skip checkpointer for persistence features
</boundaries>

<fix-thread-id-required>
Always provide thread_id in config to enable state persistence.
```typescript
// WRONG: No thread_id - state NOT persisted!
await graph.invoke({ messages: [new HumanMessage("Hello")] });
await graph.invoke({ messages: [new HumanMessage("What did I say?")] });  // Doesn't remember!

// CORRECT: Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ messages: [new HumanMessage("Hello")] }, config);
await graph.invoke({ messages: [new HumanMessage("What did I say?")] }, config);  // Remembers!
```
</fix-thread-id-required>


<fix-inmemory-not-for-production>
Use PostgresSaver instead of MemorySaver for production persistence.
```typescript
// WRONG: Data lost on process restart
const checkpointer = new MemorySaver();  // In-memory only!

// CORRECT: Use persistent storage for production
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
const checkpointer = PostgresSaver.fromConnString("postgresql://...");
await checkpointer.setup(); // only needed on first use to create tables
```
</fix-inmemory-not-for-production>

<fix-resume-with-none>
Pass null to resume from checkpoint instead of providing new input.
```typescript
// WRONG: Providing new input restarts from beginning
await graph.invoke({ messages: ["New message"] }, config);  // Restarts!

// CORRECT: Use null to resume from checkpoint
await graph.invoke(null, config);  // Continues from where it paused
```
</fix-resume-with-none>

<fix-store-injection>
Access store via config parameter in graph nodes.
```typescript
// WRONG: Store not available in node
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// CORRECT: Access store via config parameter
const myNode = async (state, config) => {
  await config.store.put(...);  // Correct store instance
};
```
</fix-store-injection>
