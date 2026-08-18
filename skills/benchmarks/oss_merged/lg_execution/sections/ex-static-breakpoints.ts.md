Set compile-time breakpoints for debugging. Not recommended for human-in-the-loop — use `interrupt()` instead.
```typescript
const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", END)
  .compile({
    checkpointer,
    interruptBefore: ["step2"],  // Pause before step2
  });

const config = { configurable: { thread_id: "1" } };
await graph.invoke({ data: "test" }, config);  // Runs until step2
await graph.invoke(null, config);  // Resume
```
