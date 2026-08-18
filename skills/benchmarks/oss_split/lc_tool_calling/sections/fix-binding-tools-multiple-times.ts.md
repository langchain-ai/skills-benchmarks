Bind all tools at once, not sequentially.

```typescript
// Problem: Binding tools overwrites previous binding
const model = new ChatOpenAI({ model: "gpt-4.1" });
const withTool1 = model.bindTools([tool1]);
const withTool2 = withTool1.bindTools([tool2]); // Only has tool2!

// Solution: Bind all tools at once
const withBothTools = model.bindTools([tool1, tool2]);
```
