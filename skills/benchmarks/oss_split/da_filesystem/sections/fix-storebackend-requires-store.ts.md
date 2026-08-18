Provide store when using StoreBackend:

```typescript
// Missing store
await createDeepAgent({ backend: (config) => new StoreBackend(config) });

// Provide store
await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
