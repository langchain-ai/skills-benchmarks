Parallel tool calls in one step:

```typescript
// Models can call multiple tools simultaneously
const agent = createAgent({
  model: "gpt-4.1",
  tools: [weatherTool, newsToolTool],
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Get weather for NYC and latest news for SF"
  }],
});

// Agent may call both tools in parallel in a single step
```
