Dynamic model selection by task:

```typescript
import { initChatModel } from "langchain";

function getModel(task: string) {
  const modelMap = {
    reasoning: "openai:gpt-5",
    fast: "google-genai:gemini-2.5-flash-lite",
    vision: "openai:gpt-4.1",
    long_context: "anthropic:claude-sonnet-4-5-20250929",
    cost_effective: "openai:gpt-4.1-mini",
  };

  return initChatModel(modelMap[task] || "openai:gpt-4.1");
}

// Usage
const reasoningModel = await getModel("reasoning");
const fastModel = await getModel("fast");
```
