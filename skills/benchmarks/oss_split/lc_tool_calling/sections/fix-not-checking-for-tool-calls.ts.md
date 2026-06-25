Check if tool_calls exist before using.

```typescript
// Problem: Assuming model always calls tools
const response = await modelWithTools.invoke("Hello");
await tool.invoke(response.tool_calls[0]); // Error if no tool calls!

// Solution: Check if tool calls exist
if (response.tool_calls && response.tool_calls.length > 0) {
  for (const toolCall of response.tool_calls) {
    await tool.invoke(toolCall);
  }
} else {
  // Model responded without calling tools
  console.log(response.content);
}
```
