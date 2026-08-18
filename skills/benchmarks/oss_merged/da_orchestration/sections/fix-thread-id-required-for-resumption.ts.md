A consistent thread_id is required to resume interrupted workflows.
```typescript
// WRONG: Can't resume without thread_id
await agent.invoke({ messages: [...] });
await agent.updateState(...);  // Which thread?

// CORRECT
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [...] }, config);
await agent.updateState(config, ...);
await agent.invoke(null, config);  // Resume
```
