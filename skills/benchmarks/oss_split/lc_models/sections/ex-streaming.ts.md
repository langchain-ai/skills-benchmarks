Stream tokens in real-time:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Stream tokens as they arrive
const stream = await model.stream("Explain quantum computing");

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```
