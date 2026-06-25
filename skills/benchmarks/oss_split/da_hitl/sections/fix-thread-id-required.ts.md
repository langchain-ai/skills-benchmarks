Use consistent thread_id to resume:

```typescript
// Can't resume without thread_id
await agent.invoke({...});
await agent.updateState(...);  // Which thread?

// Use consistent thread_id
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({...}, config);
await agent.updateState(config, ...);
```
