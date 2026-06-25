Use messages mode for token streaming:

```typescript
// Problem: Using wrong mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "updates" })) {
  console.log(chunk.content);  // Not how updates work!
}

// Solution: Use "messages" mode for tokens
for await (const chunk of await agent.stream(input, { streamMode: "messages" })) {
  const [token, metadata] = chunk;
  console.log(token.content);
}
```
