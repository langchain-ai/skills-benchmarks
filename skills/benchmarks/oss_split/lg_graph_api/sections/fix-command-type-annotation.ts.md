Specify destinations with ends option:

```typescript
// WRONG - No ends specified
const nodeA = async (state) => {
  return new Command({ goto: "nodeB" });
};

builder.addNode("nodeA", nodeA);  // Error when using Command!

// CORRECT - Specify possible destinations
builder.addNode("nodeA", nodeA, { ends: ["nodeB", "nodeC"] });
```
