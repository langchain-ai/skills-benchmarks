---
name: langgraph-memory-js
description: "[LangGraph] Memory in LangGraph: short-term (thread-scoped) vs long-term (cross-thread) memory using checkpointers and stores"
---

<overview>
LangGraph provides two types of memory for agents:
- **Short-term memory**: Thread-scoped, managed via checkpointers
- **Long-term memory**: Cross-thread, managed via stores
</overview>

<decision-table>

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single thread | Via checkpointer | Conversation history |
| Long-term | Cross-thread | Via store | User preferences, facts |

</decision-table>

<ex-short-term-memory>
```typescript
import { MemorySaver, StateGraph, StateSchema, ReducedValue, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = new StateSchema({
  messages: new ReducedValue(
    z.array(z.string()).default(() => []),
    { reducer: (current, update) => current.concat(update) }
  ),
});

const respond = async (state: typeof State.State) => {
  // Access conversation history
  const history = state.messages;
  return { messages: [`I remember ${history.length} messages`] };
};

const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("respond", respond)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer });

// First turn
const config = { configurable: { thread_id: "user-1" } };
await graph.invoke({ messages: ["Hello"] }, config);

// Second turn - remembers first
await graph.invoke({ messages: ["How are you?"] }, config);
// Response: "I remember 3 messages" (Hello, response, How are you?)
```
</ex-short-term-memory>

<ex-long-term-memory>
```typescript
import { InMemoryStore } from "@langchain/langgraph";

// Create store for long-term memory
const store = new InMemoryStore();

// Save user preference (available across all threads)
const userId = "alice";
const namespace = [userId, "preferences"];

await store.put(
  namespace,
  "language",
  { preference: "short, direct responses" }
);

// Retrieve in any thread
const getUserPrefs = async (state, config) => {
  const store = config.store;
  const userId = state.userId;
  const namespace = [userId, "preferences"];

  const prefs = await store.get(namespace, "language");
  return { preferences: prefs };
};

// Compile with store
const graph = builder.compile({
  checkpointer,
  store,
});

// Use in different threads
const thread1 = { configurable: { thread_id: "thread-1" } };
const thread2 = { configurable: { thread_id: "thread-2" } };

// Both threads access same long-term memory
await graph.invoke({ userId: "alice" }, thread1);  // Gets preferences
await graph.invoke({ userId: "alice" }, thread2);  // Same preferences
```
</ex-long-term-memory>

<ex-store-operations>
```typescript
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Put (create/update)
await store.put(
  ["user-123", "facts"],
  "location",
  { city: "San Francisco", country: "USA" }
);

// Get
const item = await store.get(["user-123", "facts"], "location");
console.log(item);  // { city: 'San Francisco', country: 'USA' }

// Search with filters
const results = await store.search(
  ["user-123", "facts"],
  { filter: { country: "USA" } }
);

// Delete
await store.delete(["user-123", "facts"], "location");
```
</ex-store-operations>

<ex-accessing-store-in-nodes>
```typescript
import { BaseStore } from "@langchain/langgraph";

const myNode = async (state, config: { store: BaseStore }) => {
  const store = config.store;
  const namespace = [state.userId, "memories"];

  // Retrieve past memories
  const memories = await store.search(namespace, { query: "preferences" });

  // Save new memory
  await store.put(
    namespace,
    "new_fact",
    { fact: "User likes TypeScript" }
  );

  return { processed: true };
};

const graph = builder.compile({
  checkpointer,
  store,
});
```
</ex-accessing-store-in-nodes>

<ex-combining-memory>
```typescript
const smartNode = async (state, config) => {
  const store = config.store;

  // Short-term: conversation context
  const recentMessages = state.messages.slice(-5);  // Last 5 messages

  // Long-term: user profile
  const userId = state.userId;
  const profile = await store.get([userId, "profile"], "info");

  // Use both for personalized response
  const response = await generateResponse(recentMessages, profile);

  return { messages: [response] };
};

const graph = new StateGraph(State)
  .addNode("respond", smartNode)
  .addEdge(START, "respond")
  .addEdge("respond", END)
  .compile({ checkpointer, store });
```
</ex-combining-memory>

<ex-persistent-stores>
```typescript
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";

// Use PostgreSQL for production
const store = await PostgresStore.fromConnString(
  "postgresql://user:pass@localhost/db"
);

const graph = builder.compile({
  checkpointer,
  store,
});
```
</ex-persistent-stores>

<boundaries>
**What You CAN Configure**

- Use checkpointers for short-term memory
- Use stores for long-term memory
- Namespace organization
- Search and filter memories
- Access store in nodes via config
- Choose store backend

**What You CANNOT Configure**

- Share short-term memory across threads
- Modify memory serialization format
- Store mechanism internals
</boundaries>

<fix-short-term-needs-checkpointer>
```typescript
// WRONG - No checkpointer, no memory
const graph = builder.compile();  // Messages lost!

// CORRECT
const checkpointer = new MemorySaver();
const graph = builder.compile({ checkpointer });
```
</fix-short-term-needs-checkpointer>

<fix-long-term-needs-store>
```typescript
// WRONG - Trying to share data without store
// Can't access data from other threads with checkpointer alone!

// CORRECT - Use store
const store = new InMemoryStore();
const graph = builder.compile({ checkpointer, store });
```
</fix-long-term-needs-store>

<fix-store-accessed-via-config>
```typescript
// WRONG - Store not available
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// CORRECT - Access via config
const myNode = async (state, config) => {
  const store = config.store;
  await store.put(...);
};
```
</fix-store-accessed-via-config>

<fix-inmemorystore-not-for-production>
```typescript
// WRONG - Data lost on restart
const store = new InMemoryStore();  // Memory only!

// CORRECT - Use persistent backend
import { PostgresStore } from "@langchain/langgraph-checkpoint-postgres";
const store = await PostgresStore.fromConnString("postgresql://...");
```
</fix-inmemorystore-not-for-production>

<fix-always-await-store-operations>
```typescript
// WRONG
const item = store.get(namespace, key);
console.log(item);  // Promise!

// CORRECT
const item = await store.get(namespace, key);
console.log(item);
```
</fix-always-await-store-operations>

<documentation-links>
- [Memory Overview](https://docs.langchain.com/oss/javascript/concepts/memory)
- [Short-Term Memory](https://docs.langchain.com/oss/javascript/langchain/short-term-memory)
- [Long-Term Memory](https://docs.langchain.com/oss/javascript/langchain/long-term-memory)
- [Store Reference](https://docs.langchain.com/oss/javascript/langgraph/persistence#memory-store)
</documentation-links>
