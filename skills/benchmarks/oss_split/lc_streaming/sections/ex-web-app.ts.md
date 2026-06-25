Express endpoint with SSE streaming:

```typescript
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

// Express.js endpoint
app.post("/api/chat", async (req, res) => {
  // Set headers for Server-Sent Events
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  try {
    for await (const [mode, chunk] of await agent.stream(
      { messages: req.body.messages },
      { streamMode: ["messages", "updates"] }
    )) {
      if (mode === "messages") {
        const [token, metadata] = chunk;
        if (token.content) {
          // Send token to client
          res.write(`data: ${JSON.stringify({ type: "token", content: token.content })}\n\n`);
        }
      } else if (mode === "updates") {
        // Send step update to client
        res.write(`data: ${JSON.stringify({ type: "step", data: chunk })}\n\n`);
      }
    }

    res.write("data: [DONE]\n\n");
    res.end();
  } catch (error) {
    res.write(`data: ${JSON.stringify({ type: "error", message: error.message })}\n\n`);
    res.end();
  }
});
```
