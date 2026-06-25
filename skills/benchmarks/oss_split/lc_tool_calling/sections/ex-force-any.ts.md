Force model to use any tool.

```typescript
// Force model to use at least one tool (any of them)
const modelWithTools = model.bindTools(
  [tool1, tool2, tool3],
  { tool_choice: "any" }
);

// Model must call at least one tool, can't respond with just text
const response = await modelWithTools.invoke("Process this data");
```
