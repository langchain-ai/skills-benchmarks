Await the stream call:

```typescript
// WRONG - Missing await
const stream = graph.stream({});
for await (const chunk of stream) {  // Error!
  console.log(chunk);
}

// CORRECT
for await (const chunk of await graph.stream({})) {
  console.log(chunk);
}
```
