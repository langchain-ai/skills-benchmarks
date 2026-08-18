Agent skips planning for simple tasks:

```typescript
// The agent won't always use write_todos for simple tasks

// Simple task - agent likely won't create todos
const result1 = await agent.invoke({
  messages: [{ role: "user", content: "What is 2+2?" }]
});
// No todos in state

// Complex task - agent will likely create todos
const result2 = await agent.invoke({
  messages: [{ role: "user", content: "Build a web scraper and analyze the data" }]
});
// Todos present in state
```
