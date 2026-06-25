Compile before invoking graph:

```typescript
// WRONG
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke({ input: "test" });  // Error!

// CORRECT
const graph = builder.compile();
await graph.invoke({ input: "test" });
```
