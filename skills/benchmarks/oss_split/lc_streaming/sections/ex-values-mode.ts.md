Get full state after each step:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [weatherTool],
});

// Get full state after each step
for await (const state of await agent.stream(
  { messages: [{ role: "user", content: "What's the weather?" }] },
  { streamMode: "values" }
)) {
  console.log("Current messages:", state.messages.length);
  console.log("Last message:", state.messages[state.messages.length - 1].content);
}
```
