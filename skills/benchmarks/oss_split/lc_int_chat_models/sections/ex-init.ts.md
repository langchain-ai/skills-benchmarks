Provider-agnostic model initialization.

```typescript
import { initChatModel } from "langchain/chat_models/universal";

// Automatically select model based on environment
const model = await initChatModel("gpt-4", {
  modelProvider: "openai",
  temperature: 0.7,
});

// Or with Bedrock
const bedrockModel = await initChatModel(
  "anthropic.claude-3-sonnet-20240229-v1:0",
  { modelProvider: "bedrock" }
);
```
