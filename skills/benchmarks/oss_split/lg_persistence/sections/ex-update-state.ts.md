Modify state before resuming:

```typescript
// Modify state before resuming
const config = { configurable: { thread_id: "1" } };

// Update state
await graph.updateState(config, { data: "manually_updated" });

// Resume with updated state
await graph.invoke(null, config);
```
