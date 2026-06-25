Reject and provide feedback to agent:

```typescript
const agent = await createDeepAgent({
  interruptOn: { deploy_code: true },
  checkpointer: new MemorySaver()
});

const config = { configurable: { thread_id: "session-1" } };

await agent.invoke({
  messages: [{ role: "user", content: "Deploy to production" }]
}, config);

// Reject
await agent.updateState(config, {
  messages: [
    new Command({
      resume: {
        decisions: [{
          type: "reject",
          message: "Tests haven't passed yet"
        }]
      }
    })
  ]
});

await agent.invoke(null, config);
```
