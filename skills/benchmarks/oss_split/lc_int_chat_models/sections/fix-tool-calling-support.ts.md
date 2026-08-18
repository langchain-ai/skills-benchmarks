Check model supports tool calling.

```typescript
// Not all models support tool calling
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This older model doesn't support tools!

// Use models with tool support
const model = new ChatOpenAI({ modelName: "gpt-4" });
const withTools = model.bindTools([myTool]);
```
