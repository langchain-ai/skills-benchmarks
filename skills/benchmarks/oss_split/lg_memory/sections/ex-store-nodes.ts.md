Access store via config:

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
