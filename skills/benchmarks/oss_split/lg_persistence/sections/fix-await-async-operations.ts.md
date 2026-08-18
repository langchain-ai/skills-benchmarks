Await all async operations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" }, config);
console.log(result.values);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" }, config);
console.log(result.values);  // Works!
```
