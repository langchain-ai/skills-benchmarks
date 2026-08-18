Stream agent steps and tokens:

```typescript
// Stream with updates mode to see each step
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for LangChain" }] },
  { streamMode: "updates" }
)) {
  console.log("Step:", chunk);
}

// Stream with messages mode for LLM tokens
for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "Search for LangChain" }] },
  { streamMode: "messages" }
)) {
  const [token, metadata] = chunk;
  if (token.content) process.stdout.write(token.content);
}
```
