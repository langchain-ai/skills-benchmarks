Files are lost when thread changes:

```typescript
// Files lost when thread changes
await agent.invoke({messages: [{role: "user", content: "Write /notes.txt"}]},
  {configurable: {thread_id: "thread-1"}});
await agent.invoke({messages: [{role: "user", content: "Read /notes.txt"}]},
  {configurable: {thread_id: "thread-2"}});
// File not found!

// Use same thread_id OR StoreBackend
```
