responseFormat extracts from final response only.

```typescript
// Problem: Using responseFormat with tools incorrectly
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
  responseFormat: MySchema,  // Will extract from FINAL response only
});
// Tools run first, then schema extracted from final response

// This is correct if you want tools + structured final output
// Just understand the flow
```
