Handle interrupts during streaming:

```typescript
const config = {
  configurable: { thread_id: "1" },
  streamMode: ["messages", "updates"] as const,
  subgraphs: true
};

for await (const [metadata, mode, chunk] of await graph.stream(
  { query: "test" },
  config
)) {
  if (mode === "messages") {
    // Handle streaming LLM content
    const [msg, _] = chunk;
    if (msg.content) {
      process.stdout.write(msg.content);
    }
  } else if (mode === "updates") {
    // Check for interrupts
    if ("__interrupt__" in chunk) {
      // Handle interrupt
      const interruptInfo = chunk.__interrupt__[0].value;
      // Get user input and resume
      break;
    }
  }
}
```
