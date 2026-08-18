Models may return multiple tool_calls at once - iterate over all of them.
```typescript
const response = await modelWithTools.invoke("Get weather for NYC and news about AI");

// Model may call both tools in parallel
console.log(response.tool_calls);
// [
//   { name: 'get_weather', args: { location: 'NYC' }, id: 'call_1' },
//   { name: 'get_news', args: { topic: 'AI' }, id: 'call_2' }
// ]

// Execute ALL tool calls, not just the first one
for (const toolCall of response.tool_calls ?? []) {
  const result = await toolsByName[toolCall.name].invoke(toolCall.args);
}
```
