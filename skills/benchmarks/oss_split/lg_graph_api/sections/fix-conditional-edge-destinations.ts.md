Add nodes before routing to them:

```typescript
// WRONG - "missingNode" not added to graph
const router = (state) => "missingNode";

builder.addConditionalEdges("nodeA", router, ["missingNode"]);

// CORRECT - Add all possible destinations
builder.addNode("missingNode", func);
builder.addConditionalEdges("nodeA", router, ["missingNode"]);
```
