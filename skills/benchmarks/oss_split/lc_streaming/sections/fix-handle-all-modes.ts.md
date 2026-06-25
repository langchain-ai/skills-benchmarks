Destructure mode in multi-mode streaming:

```typescript
// Problem: Not handling different modes
for await (const chunk of await agent.stream(
  input,
  { streamMode: ["updates", "messages"] }
)) {
  console.log(chunk);  // Which mode is this?
}

// Solution: Destructure mode
for await (const [mode, chunk] of await agent.stream(
  input,
  { streamMode: ["updates", "messages"] }
)) {
  if (mode === "messages") {
    const [token, metadata] = chunk;
    console.log(token.content);
  } else if (mode === "updates") {
    console.log("Step:", chunk);
  }
}
```
