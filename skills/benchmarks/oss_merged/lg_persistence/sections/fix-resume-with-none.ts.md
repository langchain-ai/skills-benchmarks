Pass null to resume from checkpoint instead of providing new input.
```typescript
// WRONG: Providing new input restarts from beginning
await graph.invoke({ messages: ["New message"] }, config);  // Restarts!

// CORRECT: Use null to resume from checkpoint
await graph.invoke(null, config);  // Continues from where it paused
```
