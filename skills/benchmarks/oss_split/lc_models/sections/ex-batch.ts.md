Batch process multiple inputs:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Process multiple inputs in parallel
const results = await model.batch([
  "What is AI?",
  "What is ML?",
  "What is LangChain?"
]);

results.forEach((result, i) => {
  console.log(`Answer ${i + 1}:`, result.content);
});
```
