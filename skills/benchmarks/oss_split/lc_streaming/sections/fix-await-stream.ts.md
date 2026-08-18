Await stream before iterating:

```typescript
// Problem: Missing await
const stream = agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {  // Error: stream is Promise!
  console.log(chunk);
}

// Solution: Await stream initialization
const stream = await agent.stream(input, { streamMode: "updates" });
for await (const chunk of stream) {
  console.log(chunk);
}
```
