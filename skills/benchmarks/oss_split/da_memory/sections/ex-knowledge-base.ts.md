Build persistent knowledge across sessions:

```typescript
const agent = await createDeepAgent({
  backend: (config) => new CompositeBackend(
    new StateBackend(config),
    {
      "/memories/": new StoreBackend(config),
      "/workspace/": new StateBackend(config),
    }
  ),
  store: new InMemoryStore()
});

// Build knowledge
await agent.invoke({
  messages: [{
    role: "user",
    content: "Document the DB schema in /memories/db-schema.md"
  }]
}, { configurable: { thread_id: "thread-1" } });

// Use knowledge later
await agent.invoke({
  messages: [{
    role: "user",
    content: "Write a migration to add email to users"
  }]
}, { configurable: { thread_id: "thread-2" } });
```
