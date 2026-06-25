Buffer tokens for smoother UI updates:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

let buffer = "";
const stream = await model.stream("Write a long essay");

for await (const chunk of stream) {
  buffer += chunk.content;

  // Update UI every 10 characters or on complete words
  if (buffer.length >= 10 || chunk.content.includes(" ")) {
    console.log(buffer);
    buffer = "";
  }
}

// Flush remaining buffer
if (buffer) {
  console.log(buffer);
}
```
