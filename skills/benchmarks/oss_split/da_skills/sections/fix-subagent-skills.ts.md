Provide skills to subagents explicitly:

```typescript
// No inherited skills
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{ name: "helper", ... }]
});

// Provide skills explicitly
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{
    name: "helper",
    skills: ["/helper-skills/"],
    ...
  }]
});
```
