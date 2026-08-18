Fix missing API key:

```typescript
// Problem: Missing API key
const model = await initChatModel("openai:gpt-4.1");
await model.invoke("Hello"); // Error: API key not found

// Solution: Set environment variable
process.env.OPENAI_API_KEY = "sk-...";
const model = await initChatModel("openai:gpt-4.1");

// OR pass directly
import { ChatOpenAI } from "@langchain/openai";
const model = new ChatOpenAI({
  model: "gpt-4.1",
  apiKey: "sk-...",
});
```
