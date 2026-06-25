Stream responses with interrupt handling.

```typescript
const config = { configurable: { thread_id: "session-4" } };

// Stream until interrupt
for await (const [mode, chunk] of await agent.stream(
  { messages: [{ role: "user", content: "Send report to team" }] },
  { ...config, streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    const [token, metadata] = chunk;
    if (token.content) {
      process.stdout.write(token.content);
    }
  } else if (mode === "updates") {
    if ("__interrupt__" in chunk) {
      console.log("\nWaiting for approval...");
      break;  // Handle interrupt
    }
  }
}

// Resume after approval
for await (const [mode, chunk] of await agent.stream(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  { ...config, streamMode: ["messages"] }
)) {
  // Continue streaming
}
```
