Persist state across conversations:

```typescript
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool], checkpointer });

const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);

// Later conversation - agent remembers
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Response: "Your name is Alice"
```
