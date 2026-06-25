Multi-turn conversation with history:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Build conversation history
const messages = [
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "What's the capital of France?" },
];

const response1 = await model.invoke(messages);
messages.push({ role: "assistant", content: response1.content });

// Continue conversation
messages.push({ role: "user", content: "What's its population?" });
const response2 = await model.invoke(messages);

console.log(response2.content); // Knows we're talking about Paris
```
