Check model capabilities:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Check if model supports features
console.log("Supports streaming:", typeof model.stream === "function");
console.log("Supports tool calling:", typeof model.bindTools === "function");
console.log("Supports structured output:", typeof model.withStructuredOutput === "function");
```
