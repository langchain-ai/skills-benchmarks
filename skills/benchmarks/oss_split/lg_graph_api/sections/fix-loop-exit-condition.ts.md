Add exit condition to loops:

```typescript
// WRONG - Infinite loop
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // No way out!

// CORRECT - Conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) return END;
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue, ["nodeB", END]);
```
