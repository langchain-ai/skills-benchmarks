Access saved preferences across threads:

```typescript
import { createDeepAgent, CompositeBackend, StateBackend, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";

const store = new InMemoryStore();

const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    { "/memories/": new StoreBackend(config) }
  ),
  store
});

// Thread 1: Save preferences
await agent.invoke({
  messages: [{ role: "user", content: "Save my preference: concise explanations to /memories/prefs.txt" }]
}, { configurable: { thread_id: "thread-1" } });

// Thread 2: Access preferences
await agent.invoke({
  messages: [{ role: "user", content: "Read my preferences and explain async/await" }]
}, { configurable: { thread_id: "thread-2" } });
```
