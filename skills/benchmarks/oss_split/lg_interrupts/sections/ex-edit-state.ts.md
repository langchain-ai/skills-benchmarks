Modify state before resuming:

```typescript
const config = { configurable: { thread_id: "1" } };

// Run until interrupt
await graph.invoke({ data: "test" }, config);

// Modify state before resuming
await graph.updateState(config, { data: "manually edited" });

// Resume with edited state
await graph.invoke(null, config);
```
