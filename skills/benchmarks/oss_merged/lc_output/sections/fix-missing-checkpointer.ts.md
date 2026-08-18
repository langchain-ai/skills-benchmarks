HITL requires a checkpointer to persist state.
```typescript
// WRONG
const agent = createAgent({ model: "gpt-4.1", tools: [sendEmail], interruptBefore: ["send_email"] });

// CORRECT
const agent = createAgent({
  model: "gpt-4.1", tools: [sendEmail],
  checkpointer: new MemorySaver(),  // Required
  interruptBefore: ["send_email"]
});
```
