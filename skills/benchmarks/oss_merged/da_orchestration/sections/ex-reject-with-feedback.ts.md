Reject a pending action with feedback, prompting the agent to try a different approach.
```typescript
await agent.updateState(config, {
  messages: [new Command({ resume: { decisions: [{ type: "reject", message: "Run tests first" }] } })]
});
const result = await agent.invoke(null, config);
```
