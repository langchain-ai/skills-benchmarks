Add timeout handling for slow streams:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [slowTool],
});

async function streamWithTimeout(timeoutMs: number) {
  const timeout = setTimeout(() => {
    throw new Error(`Stream timeout after ${timeoutMs}ms`);
  }, timeoutMs);

  try {
    for await (const chunk of await agent.stream(
      { messages: [{ role: "user", content: "Do something slow" }] },
      { streamMode: "updates" }
    )) {
      clearTimeout(timeout);
      console.log(chunk);

      // Reset timeout for next chunk
      timeout.setTimeout(() => {
        throw new Error(`Stream timeout after ${timeoutMs}ms`);
      }, timeoutMs);
    }
  } finally {
    clearTimeout(timeout);
  }
}
```
