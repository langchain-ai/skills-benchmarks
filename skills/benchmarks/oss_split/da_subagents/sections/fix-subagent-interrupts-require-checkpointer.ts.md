Add checkpointer to main agent:

```typescript
// Missing checkpointer
await createDeepAgent({
  subagents: [{
    name: "deployer",
    interruptOn: { deploy: true }
  }]
});

// Checkpointer on main agent
await createDeepAgent({
  subagents: [{
    name: "deployer",
    interruptOn: { deploy: true }
  }],
  checkpointer: new MemorySaver()
});
```
