Must compile() to get executable graph.
```typescript
// WRONG
await builder.invoke({ input: "test" });

// CORRECT
const graph = builder.compile();
await graph.invoke({ input: "test" });
```
