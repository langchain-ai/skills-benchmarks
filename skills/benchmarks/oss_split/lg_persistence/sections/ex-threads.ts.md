Isolated state per thread:

```typescript
// Different threads maintain separate state
const thread1Config = { configurable: { thread_id: "user-alice" } };
const thread2Config = { configurable: { thread_id: "user-bob" } };

// Alice's conversation
await graph.invoke({ messages: ["Hi from Alice"] }, thread1Config);

// Bob's conversation (separate state)
await graph.invoke({ messages: ["Hi from Bob"] }, thread2Config);

// Alice's state is isolated from Bob's
```
