Anthropic Claude with tool binding.

```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({
  modelName: "claude-3-opus-20240229",
  temperature: 0.7,
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  maxTokens: 1024,
});

// Long context usage
const response = await model.invoke([
  { role: "user", content: "Analyze this long document..." }
]);

// With tool use
const modelWithTools = model.bindTools([
  {
    name: "get_weather",
    description: "Get weather for a location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string" }
      },
      required: ["location"]
    }
  }
]);
```
