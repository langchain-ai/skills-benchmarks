Access store in custom tools:

```typescript
import { tool } from "langchain";
import { createAgent } from "langchain";
import { InMemoryStore } from "@langchain/langgraph";
import { z } from "zod";

const getUserPreference = tool(
  async ({ key }) => {
    const value = await store.get(["user_prefs"], key);
    return value ? String(value) : "Not found";
  },
  {
    name: "get_user_preference",
    description: "Get a user preference",
    schema: z.object({ key: z.string() }),
  }
);

const saveUserPreference = tool(
  async ({ key, value }) => {
    await store.put(["user_prefs"], key, { value });
    return `Saved ${key}=${value}`;
  },
  {
    name: "save_user_preference",
    description: "Save a user preference",
    schema: z.object({ key: z.string(), value: z.string() }),
  }
);

const store = new InMemoryStore();

const agent = createAgent({
  model: "gpt-4.1",
  tools: [getUserPreference, saveUserPreference],
  store
});

// First session
await agent.invoke({
  messages: [{ role: "user", content: "Remember I prefer dark mode" }]
});

// Second session
await agent.invoke({
  messages: [{ role: "user", content: "What UI theme do I prefer?" }]
});
```
