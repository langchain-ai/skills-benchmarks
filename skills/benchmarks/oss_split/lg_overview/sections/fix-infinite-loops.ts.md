Add conditional exit to loops:

```typescript
// WRONG - Loop without exit condition
builder
  .addEdge("nodeA", "nodeB")
  .addEdge("nodeB", "nodeA");  // Infinite loop!

// CORRECT - Add conditional edge to END
const shouldContinue = (state) => {
  if (state.count > 10) {
    return END;
  }
  return "nodeB";
};

builder.addConditionalEdges("nodeA", shouldContinue);
```
