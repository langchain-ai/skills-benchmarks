Add store for cross-thread memory:

```typescript
// WRONG - Trying to share data without store
// Can't access data from other threads with checkpointer alone!

// CORRECT - Use store
const store = new InMemoryStore();
const graph = builder.compile({ checkpointer, store });
```
