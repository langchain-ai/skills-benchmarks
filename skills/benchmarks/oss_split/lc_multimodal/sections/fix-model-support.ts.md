Switch from text-only to vision-capable model.

```typescript
// Problem: Using text-only model
const model = new ChatOpenAI({ model: "gpt-3.5-turbo" });
await model.invoke([imageMessage]);  // Error!

// Solution: Use vision-capable model
const model = new ChatOpenAI({ model: "gpt-4.1" });
```
