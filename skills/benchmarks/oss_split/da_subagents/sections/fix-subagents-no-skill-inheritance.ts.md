Provide skills to subagent explicitly:

```typescript
// Subagent won't have main skills
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
