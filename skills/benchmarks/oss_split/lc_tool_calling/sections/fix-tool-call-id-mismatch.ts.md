Match tool_call_id from the response.

```typescript
// Problem: Wrong tool_call_id
const response = await modelWithTools.invoke("Get weather");
const toolMessage = new ToolMessage({
  content: "Sunny",
  tool_call_id: "wrong_id", // Doesn't match!
  name: "get_weather",
});

// Solution: Use correct ID from tool call
const toolMessage = new ToolMessage({
  content: "Sunny",
  tool_call_id: response.tool_calls[0].id, // Correct ID
  name: "get_weather",
});

// OR use tool.invoke() which handles this automatically
const toolMessage = await getTool.invoke(response.tool_calls[0]);
```
