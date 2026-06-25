Incremental state deltas:

```typescript
// Stream only the changes
for await (const chunk of await graph.stream(
  { count: 0 },
  { streamMode: "updates" }
)) {
  console.log(chunk);  // { process: { count: 1 } }
}
```
