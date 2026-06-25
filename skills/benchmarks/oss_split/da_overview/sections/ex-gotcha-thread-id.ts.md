Use thread_id for conversation continuity:

```typescript
// Each invocation is isolated without thread_id
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// Use consistent thread_id for conversation continuity
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] }, config);
```
