Always await async invocations:

```typescript
// WRONG - Forgetting await
const result = agent.invoke(...);  // Returns Promise!
console.log(result.messages);  // undefined

// CORRECT - Always await
const result = await agent.invoke(...);
console.log(result.messages);  // Works!
```
