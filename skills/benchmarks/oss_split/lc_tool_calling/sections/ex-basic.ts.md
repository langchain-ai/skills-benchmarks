Define tool and bind to model.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";
import { z } from "zod";

// Define a tool
const getWeather = tool(
  async ({ location }: { location: string }) => {
    return `Weather in ${location}: Sunny, 72F`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location",
    schema: z.object({
      location: z.string().describe("City name"),
    }),
  }
);

// Bind tool to model
const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getWeather]);

// Model will decide to call the tool
const response = await modelWithTools.invoke(
  "What's the weather in San Francisco?"
);

// Check if model called a tool
console.log(response.tool_calls);
// [{
//   name: "get_weather",
//   args: { location: "San Francisco" },
//   id: "call_abc123"
// }]
```
