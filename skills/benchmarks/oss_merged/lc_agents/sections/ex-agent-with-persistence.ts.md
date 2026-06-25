Create a React agent with MemorySaver checkpointer for conversation persistence across invokes.
```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [search],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);

const result = await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Response: "Your name is Alice"
```
