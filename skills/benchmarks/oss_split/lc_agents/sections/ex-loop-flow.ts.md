Agent loop handles multi-step tasks:

```typescript
const agent = createAgent({ model: "gpt-4.1", tools: [searchTool, weatherTool] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for the capital of France, then get its weather" }],
});
```
