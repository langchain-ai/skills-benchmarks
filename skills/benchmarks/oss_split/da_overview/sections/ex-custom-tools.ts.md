Add custom tools to agent:

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const getWeather = tool(
  ({ city }) => `It is always sunny in ${city}`,
  {
    name: "get_weather",
    description: "Get the weather for a given city",
    schema: z.object({
      city: z.string(),
    }),
  }
);

const agent = await createDeepAgent({
  tools: [getWeather],
  systemPrompt: "You are a helpful weather assistant"
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "What's the weather in Tokyo?" }
  ]
});
```
