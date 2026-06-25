Handle interrupts while streaming:

```typescript
const config = {
  configurable: { thread_id: "1" },
  streamMode: ["updates", "messages"] as const,
};

for await (const [mode, chunk] of await graph.stream({ query: "test" }, config)) {
  if (mode === "updates") {
    if ("__interrupt__" in chunk) {
      // Handle interrupt
      const interruptInfo = chunk.__interrupt__[0].value;
      const userInput = await getUserInput(interruptInfo);

      // Resume
      await graph.invoke(new Command({ resume: userInput }), config);
      break;
    }
  }
}
```
