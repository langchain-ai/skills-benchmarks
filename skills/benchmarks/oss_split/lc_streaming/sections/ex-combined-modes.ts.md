Stream tokens and progress together:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Stream both LLM tokens AND agent progress
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Research LangChain" }] },
  { streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    // LLM token stream
    const [token, metadata] = chunk;
    if (token.content) {
      process.stdout.write(token.content);
    }
  } else if (mode === "updates") {
    // Agent step updates
    console.log("\nStep update:", chunk);
  }
}
```
