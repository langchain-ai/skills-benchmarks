Use consistent thread_id to maintain conversation context across invocations.
```typescript
// WRONG: Each invocation is isolated
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// CORRECT
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [...] }, config);
await agent.invoke({ messages: [...] }, config);
```
