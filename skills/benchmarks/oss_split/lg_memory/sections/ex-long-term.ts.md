Cross-thread memory with store:

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
