Stream state updates and tokens:

```typescript
// Stream state updates
for await (const chunk of await agent.stream(
  { messages: [new HumanMessage("Calculate 5 + 3")] },
  { streamMode: "updates" }
)) {
  console.log(chunk);
}

// Stream LLM tokens
for await (const chunk of await agent.stream(
  { messages: [new HumanMessage("Hello!")] },
  { streamMode: "messages" }
)) {
  console.log(chunk);
}

// Multiple stream modes
for await (const [mode, chunk] of await agent.stream(
  { messages: [new HumanMessage("Help me")] },
  { streamMode: ["updates", "messages"] }
)) {
  console.log(`${mode}:`, chunk);
}
```
