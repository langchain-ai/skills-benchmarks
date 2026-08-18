Always await graph.invoke() - it returns a Promise.
```typescript
// WRONG
const result = graph.invoke({ input: "test" });  // Promise!

// CORRECT
const result = await graph.invoke({ input: "test" });
```
