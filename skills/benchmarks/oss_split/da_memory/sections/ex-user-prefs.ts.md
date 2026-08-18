Save and access preferences across threads:

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
const config1 = { configurable: { thread_id: "thread-1" } };
await agent.invoke({
  messages: [{
    role: "user",
    content: "Save my coding style to /memories/style.txt: TypeScript, async/await, Jest"
  }]
}, config1);

// Thread 2: Access preferences
const config2 = { configurable: { thread_id: "thread-2" } };
await agent.invoke({
  messages: [{
    role: "user",
    content: "Read my preferences and write a user fetch function"
  }]
}, config2);
// Agent reads /memories/style.txt
```
