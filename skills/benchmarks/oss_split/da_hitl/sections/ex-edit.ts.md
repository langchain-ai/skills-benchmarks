Modify tool arguments before executing:

```typescript
const agent = await createDeepAgent({
  interruptOn: { execute_sql: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

// Invoke
await agent.invoke({
  messages: [{ role: "user", content: "Delete old users" }]
}, config);

// Edit SQL
await agent.updateState(config, {
  messages: [
    new Command({
      resume: {
        decisions: [{
          type: "edit",
          editedAction: {
            name: "execute_sql",
            args: {
              query: "DELETE FROM users WHERE last_login < '2020-01-01' LIMIT 100"
            }
          }
        }]
      }
    })
  ]
});

// Continue
await agent.invoke(null, config);
```
