Stream agent steps with updates mode:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
});

// Stream agent steps with "updates" mode
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for AI news and summarize" }] },
  { streamMode: "updates" }
)) {
  console.log("Step:", JSON.stringify(chunk, null, 2));
}
// Shows each step: model call, tool execution, final response
```
