Compile graph before invoking:

```typescript
// WRONG - StateGraph is not executable
const builder = new StateGraph(State).addNode("node", func);
await builder.invoke(...);  // Error!

// CORRECT - Must compile first
const graph = builder.compile();
await graph.invoke(...);
```
