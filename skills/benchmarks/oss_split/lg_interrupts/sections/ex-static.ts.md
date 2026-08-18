Compile-time breakpoints:

```typescript
const checkpointer = new MemorySaver();

const graph = new StateGraph(State)
  .addNode("step1", step1)
  .addNode("step2", step2)
  .addNode("step3", step3)
  .addEdge(START, "step1")
  .addEdge("step1", "step2")
  .addEdge("step2", "step3")
  .addEdge("step3", END)
  .compile({
    checkpointer,
    interruptBefore: ["step2"],  // Pause before step2
    interruptAfter: ["step3"],   // Pause after step3
  });

const config = { configurable: { thread_id: "1" } };

// Run until first breakpoint
await graph.invoke({ data: "test" }, config);

// Resume (pauses at next breakpoint)
await graph.invoke(null, config);  // null = resume

// Resume again
await graph.invoke(null, config);
```
