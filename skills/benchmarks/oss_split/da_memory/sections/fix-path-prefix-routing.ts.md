Use correct path prefix for persistence:

```typescript
// Not persistent (wrong path)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /prefs.txt" }]
});

// Persistent (matches /memories/ route)
await agent.invoke({
  messages: [{ role: "user", content: "Save to /memories/prefs.txt" }]
});
```
