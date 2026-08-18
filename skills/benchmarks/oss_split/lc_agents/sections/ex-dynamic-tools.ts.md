Tools that depend on runtime state:

```typescript
const agent = createAgent({
  model: "gpt-4.1",
  tools: (state) => {
    const userId = state.config?.configurable?.user_id;
    return [getUserSpecificTool(userId), commonTool];
  },
});
```
