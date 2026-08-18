Use a Store for cross-thread memory to share user preferences across conversations.
```typescript
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

// Save user preference (available across ALL threads)
await store.put(["alice", "preferences"], "language", { preference: "short responses" });

// Node with store - access via config
const respond = async (state: typeof State.State, config: any) => {
  const item = await config.store.get(["alice", "preferences"], "language");
  return { response: `Using preference: ${item?.value?.preference}` };
};

// Compile with BOTH checkpointer and store
const graph = builder.compile({ checkpointer, store });

// Both threads access same long-term memory
await graph.invoke({ userId: "alice" }, { configurable: { thread_id: "thread-1" } });
await graph.invoke({ userId: "alice" }, { configurable: { thread_id: "thread-2" } });  // Same preferences!
```
