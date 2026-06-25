Combine multiple stream modes:

```typescript
// Stream multiple modes simultaneously
for await (const [mode, chunk] of await graph.stream(
  { messages: [new HumanMessage("Hi")] },
  { streamMode: ["updates", "messages", "custom"] }
)) {
  console.log(`${mode}:`, chunk);
}
```
