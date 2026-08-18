Initialize OpenAI chat model and stream responses.

```typescript
import { ChatOpenAI } from "@langchain/openai";

// Basic initialization
const model = new ChatOpenAI({
  modelName: "gpt-4",
  temperature: 0.7,
  openAIApiKey: process.env.OPENAI_API_KEY, // Optional if set in env
});

// Invoke the model
const response = await model.invoke([
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "What is LangChain?" }
]);

console.log(response.content);

// Streaming responses
const stream = await model.stream("Tell me a story");
for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```
