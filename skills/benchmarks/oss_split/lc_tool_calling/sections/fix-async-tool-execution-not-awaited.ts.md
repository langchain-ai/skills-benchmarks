Await async tools with Promise.all.

```typescript
// Problem: Not awaiting async tool
const toolResults = response.tool_calls.map(async (tc) => {
  return await tool.invoke(tc); // Returns Promise!
});
messages.push(...toolResults); // Pushing Promises, not results!

// Solution: Use Promise.all or for...of
const toolResults = await Promise.all(
  response.tool_calls.map(tc => tool.invoke(tc))
);
messages.push(...toolResults);

// Or with for...of
const toolResults = [];
for (const toolCall of response.tool_calls) {
  const result = await tool.invoke(toolCall);
  toolResults.push(result);
}
```
