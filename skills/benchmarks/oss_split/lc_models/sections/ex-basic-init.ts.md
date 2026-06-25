Universal model initialization:

```typescript
import { initChatModel } from "langchain";

// Universal initialization - easiest way
const model = await initChatModel("openai:gpt-4.1");

// Or with provider shorthand
const model2 = await initChatModel("gpt-4.1"); // Defaults to OpenAI

// Set API key (usually from environment)
process.env.OPENAI_API_KEY = "your-api-key";
const model3 = await initChatModel("openai:gpt-4.1");
```
