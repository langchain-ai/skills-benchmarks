Path must match CompositeBackend route prefix for persistence.
```typescript
// With routes: { "/memories/": StoreBackend }:
await agent.invoke(...);  // /prefs.txt -> ephemeral (no match)
await agent.invoke(...);  // /memories/prefs.txt -> persistent (matches route)
```
