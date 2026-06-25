Access store via config:

```typescript
// WRONG - Store not available
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// CORRECT - Access via config
const myNode = async (state, config) => {
  const store = config.store;
  await store.put(...);
};
```
