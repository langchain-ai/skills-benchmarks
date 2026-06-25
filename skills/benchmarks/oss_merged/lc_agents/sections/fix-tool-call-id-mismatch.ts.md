ToolMessage tool_call_id must match the original request.
```typescript
// WRONG
new ToolMessage({ content: "Sunny", tool_call_id: "wrong_id", name: "get_weather" });

// CORRECT: Use ID from tool call (or let tool.invoke handle it)
new ToolMessage({ content: "Sunny", tool_call_id: response.tool_calls[0].id, name: "get_weather" });
await getWeather.invoke(response.tool_calls[0]);  // Automatic
```
