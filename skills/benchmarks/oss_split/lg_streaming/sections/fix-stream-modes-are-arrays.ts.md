Use array for multiple modes:

```typescript
// WRONG - Single string with comma
await graph.stream({}, { streamMode: "updates, messages" });

// CORRECT - Array
await graph.stream({}, { streamMode: ["updates", "messages"] });
```
