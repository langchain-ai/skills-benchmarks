Edit tool arguments before execution.

```typescript
const result2 = await agent.invoke(
  new Command({
    resume: {
      decisions: [{ type: "edit", editedAction: { name: "send_email", args: { to: "alice@company.com", subject: "Updated", body: "..." } } }],
    },
  }),
  config
);
```
