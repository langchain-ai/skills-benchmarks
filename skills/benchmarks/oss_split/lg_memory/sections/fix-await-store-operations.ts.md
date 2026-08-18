Await async store operations:

```typescript
// WRONG
const item = store.get(namespace, key);
console.log(item);  // Promise!

// CORRECT
const item = await store.get(namespace, key);
console.log(item);
```
