Handle errors during streaming:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [riskyTool],
});

try {
  for await (const chunk of await agent.stream(
    { messages: [{ role: "user", content: "Do risky operation" }] },
    { streamMode: "updates" }
  )) {
    // Check for errors in updates
    if ("__error__" in chunk) {
      console.error("Error in stream:", chunk.__error__);
      break;
    }

    console.log("Update:", chunk);
  }
} catch (error) {
  console.error("Stream error:", error);
}
```
