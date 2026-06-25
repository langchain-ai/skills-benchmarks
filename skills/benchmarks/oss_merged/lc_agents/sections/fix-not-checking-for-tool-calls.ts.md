Check if tool_calls exist before executing.
```typescript
// WRONG: Assuming model always calls tools
await tool.invoke(response.tool_calls[0].args);  // Error!

// CORRECT
if (response.tool_calls?.length) {
  for (const toolCall of response.tool_calls) await tool.invoke(toolCall.args);
} else {
  console.log(response.content);
}
```
