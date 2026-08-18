Define custom tool with Zod schema validation.

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// Define custom tool
const weatherTool = tool(
  async ({ location, unit = "celsius" }) => {
    // Your implementation
    const data = await fetchWeather(location, unit);
    return `The weather in ${location} is ${data.temp}°${unit === "celsius" ? "C" : "F"}`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location. Use this when users ask about weather.",
    schema: z.object({
      location: z.string().describe("The city name, e.g., 'San Francisco'"),
      unit: z.enum(["celsius", "fahrenheit"]).optional().describe("Temperature unit"),
    }),
  }
);

// Use with agent
const agent = createAgent({
  model: "gpt-4.1",
  tools: [weatherTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in London?" }]
});
```
