Reject tool call with feedback.

```typescript
const result2 = await agent.invoke(
  new Command({
    resume: { decisions: [{ type: "reject", feedback: "Cannot delete without manager approval" }] },
  }),
  config
);
```
