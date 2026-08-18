Agent with custom system prompt:

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculatorTool],
  systemPrompt: `You are a helpful research assistant.
Always cite your sources when using the search tool.
Show your work when performing calculations.`,
});
```
