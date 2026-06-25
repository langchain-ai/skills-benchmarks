LLM call required for token streaming:

```typescript
// WRONG - No LLM called, nothing streamed
const node = async (state) => ({ output: "static text" });

for await (const chunk of await graph.stream({}, { streamMode: "messages" })) {
  console.log(chunk);  // Nothing!
}

// CORRECT - LLM invoked
const node = async (state) => {
  const response = await model.invoke(state.messages);  // LLM call
  return { messages: [response] };
};
```
