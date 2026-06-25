Use thread_id for persistence:

```typescript
// Todo list won't persist without thread_id
await agent.invoke({ messages: [{ role: "user", content: "Task 1" }] });
await agent.invoke({ messages: [{ role: "user", content: "Task 2" }] });

// Use thread_id for persistence
const config = { configurable: { thread_id: "user-session" } };
await agent.invoke({ messages: [{ role: "user", content: "Task 1" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "Task 2" }] }, config);
```
