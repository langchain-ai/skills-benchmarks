Choose models with sufficient context window.

```typescript
// Exceeding context limits
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo" }); // 4k context
const longText = "...".repeat(10000);
await model.invoke(longText); // Will fail!

// Use appropriate models for long context
const model = new ChatOpenAI({ modelName: "gpt-4-turbo" }); // 128k context
// OR
const model = new ChatAnthropic({
  modelName: "claude-3-opus-20240229" // 200k context
});
```
