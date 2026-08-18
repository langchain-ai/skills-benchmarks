Fix model name format:

```typescript
// Problem: Wrong model name
const model = await initChatModel("gpt4"); // Error!

// Solution: Use correct format
const model = await initChatModel("openai:gpt-4.1");
// Or provider shorthand
const model2 = await initChatModel("gpt-4.1");
```
