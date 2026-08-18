Always provide `thread_id` in config. Without it, the agent can't track state across invoke calls.

Include thread_id in config.

```typescript
// Problem: Missing thread_id
await agent.invoke(input);  // No config!

// Solution: Always provide thread_id
await agent.invoke(input, {
  configurable: { thread_id: "user-123" }
});
```
