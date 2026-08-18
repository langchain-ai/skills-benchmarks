Stream tokens as they arrive:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4.1" });

// Stream tokens as they arrive
const stream = await model.stream("Explain quantum computing in simple terms");

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
// Output appears progressively: "Quantum" "computing" "is" ...
```
