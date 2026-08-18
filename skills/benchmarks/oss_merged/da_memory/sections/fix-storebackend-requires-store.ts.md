StoreBackend requires a store instance.
```typescript
// WRONG
const agent = await createDeepAgent({ backend: (c) => new StoreBackend(c) });

// CORRECT
const agent = await createDeepAgent({ backend: (c) => new StoreBackend(c), store: new InMemoryStore() });
```
