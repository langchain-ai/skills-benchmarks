Provide store when using StoreBackend:

```typescript
// StoreBackend needs a Store
import { StoreBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// Pass a Store instance
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
