StoreBackend requires a Store instance for persistent memory across threads.
```typescript
// WRONG
const agent = await createDeepAgent({ backend: (config) => new StoreBackend(config) });

// CORRECT
const agent = await createDeepAgent({ backend: (config) => new StoreBackend(config), store: new InMemoryStore() });
```
