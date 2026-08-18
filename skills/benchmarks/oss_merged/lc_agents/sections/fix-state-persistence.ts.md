Add checkpointer and thread_id to enable conversation memory.
```typescript
// WRONG: No checkpointer - each invoke is isolated
const agent = createAgent({ model: "gpt-4.1", tools: [search] });

// CORRECT
const agent = createAgent({ model: "gpt-4.1", tools: [search], checkpointer: new MemorySaver() });
const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [...] }, config);
```
