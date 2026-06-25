Always pass tool results back to model.

```typescript
// Problem: Not passing tool results back to model
const response1 = await modelWithTools.invoke(messages);
const toolResult = await tool.invoke(response1.tool_calls[0]);
// Missing: passing result back to model!

// Solution: Always pass results back
messages.push(response1); // AI message with tool calls
messages.push(toolResult); // Tool result
const response2 = await modelWithTools.invoke(messages);
```
