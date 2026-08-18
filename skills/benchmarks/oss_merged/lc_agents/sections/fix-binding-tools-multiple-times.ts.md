Bind all tools at once - chaining bindTools overwrites previous.
```typescript
// WRONG: Only has tool2
const withTool2 = model.bindTools([tool1]).bindTools([tool2]);

// CORRECT
const withBothTools = model.bindTools([tool1, tool2]);
```
