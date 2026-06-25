Await async invocations:

```typescript
// WRONG
const result = graph.invoke({}, config);
console.log(result);  // Promise!

// CORRECT
const result = await graph.invoke({}, config);
console.log(result);
```
