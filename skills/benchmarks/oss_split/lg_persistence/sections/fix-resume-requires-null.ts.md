Use null to resume from checkpoint:

```typescript
// WRONG - Providing input restarts
await graph.invoke({ new: "data" }, config);  // Restarts from beginning

// CORRECT - Use null to resume
await graph.invoke(null, config);  // Resumes from checkpoint
```
