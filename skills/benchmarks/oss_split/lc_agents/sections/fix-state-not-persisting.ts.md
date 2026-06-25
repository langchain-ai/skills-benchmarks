Add checkpointer for conversation memory:

```typescript
// Problem: No checkpointer
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Each invoke is isolated - no memory
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember "Bob"

// Solution: Add checkpointer and thread_id
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi, I'm Bob" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Bob"
```
