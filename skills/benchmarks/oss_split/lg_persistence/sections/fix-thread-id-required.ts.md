Provide thread_id for persistence:

```typescript
// WRONG - No thread_id, state not saved
await graph.invoke({ data: "test" });  // Lost after execution!

// CORRECT - Always provide thread_id
const config = { configurable: { thread_id: "session-1" } };
await graph.invoke({ data: "test" }, config);
```
