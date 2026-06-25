Per-tool HITL policy configuration.

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: [sendEmail, readEmail, deleteEmail],
  checkpointer: new MemorySaver(),
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        send_email: { allowedDecisions: ["approve", "edit", "reject"] },
        delete_email: { allowedDecisions: ["approve", "reject"] },  // No edit
        read_email: false,  // No HITL for reading
      },
    }),
  ],
});
```
