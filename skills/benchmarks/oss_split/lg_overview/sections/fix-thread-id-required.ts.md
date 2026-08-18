Provide thread_id for persistence:

```typescript
// WRONG - No thread_id with checkpointer
await agent.invoke({ messages: [...] });  // State not persisted!

// CORRECT - Always provide thread_id
await agent.invoke(
  { messages: [...] },
  { configurable: { thread_id: "user-123" } }
);
```
