Stream from nested graphs:

```typescript
// Include subgraph outputs
for await (const chunk of await graph.stream(
  { data: "test" },
  {
    streamMode: "updates",
    subgraphs: true  // Stream from nested graphs too
  }
)) {
  console.log(chunk);
}
```
