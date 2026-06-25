Configure model parameters:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-4.1",

  // Control randomness (0 = deterministic, 1 = creative)
  temperature: 0.7,

  // Limit response length
  maxTokens: 500,

  // Alternative sampling method
  topP: 0.9,

  // Penalize repetition
  frequencyPenalty: 0.5,
  presencePenalty: 0.5,

  // Stop generation at these strings
  stop: ["\n\n", "END"],

  // Timeout for requests
  timeout: 30000, // 30 seconds

  // Max retries on failure
  maxRetries: 3,
});
```
