Always pass tool results back to the model.
```typescript
// WRONG: Missing results
const response1 = await modelWithTools.invoke(messages);
const toolResult = await tool.invoke(response1.tool_calls[0].args);

// CORRECT
messages.push(response1);
messages.push(new ToolMessage({ content: toolResult, tool_call_id: response1.tool_calls[0].id }));
const response2 = await modelWithTools.invoke(messages);
```
