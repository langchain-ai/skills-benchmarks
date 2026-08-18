Longer prefixes take precedence:

```typescript
const backend = (config) => new CompositeBackend(
  new StateBackend(config),
  {
    "/mem/": new StoreBackend(config),
    "/mem/temp/": new StateBackend(config),  // More specific
  }
);

// /mem/file.txt -> StoreBackend
// /mem/temp/file.txt -> StateBackend (longer match)
```
