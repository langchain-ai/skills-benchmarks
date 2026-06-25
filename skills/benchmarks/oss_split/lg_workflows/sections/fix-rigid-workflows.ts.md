Add error handling paths:

```typescript
// ANTI-PATTERN - Overly rigid workflow
.addEdge("validate", "process")  // Always proceeds, no error handling

// BETTER - Add conditional logic
const routeAfterValidate = (state) => {
  if (!state.validated) return "errorHandler";
  return "process";
};

.addConditionalEdges("validate", routeAfterValidate, ["process", "errorHandler"]);
```
