Provide thread_id for resuming:

```typescript
// WRONG - No thread_id
await graph.invoke({ data: "test" });  // Can't resume!

// CORRECT
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```
