Await async invocations:

```typescript
// WRONG - Forgetting await
const result = graph.invoke({ data: "test" });
console.log(result.output);  // undefined!

// CORRECT
const result = await graph.invoke({ data: "test" });
console.log(result.output);  // Works!
```
