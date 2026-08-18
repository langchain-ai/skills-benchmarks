Access store via config parameter in graph nodes.
```typescript
// WRONG: Store not available in node
const myNode = async (state) => {
  store.put(...);  // ReferenceError!
};

// CORRECT: Access store via config parameter
const myNode = async (state, config) => {
  await config.store.put(...);  // Correct store instance
};
```
