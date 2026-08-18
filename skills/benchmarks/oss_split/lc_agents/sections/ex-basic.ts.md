Basic agent with search and weather tools:

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const searchTool = tool(
  async ({ query }: { query: string }) => `Results for: ${query}`,
  {
    name: "search",
    description: "Search for information on the web",
    schema: z.object({ query: z.string().describe("The search query") }),
  }
);

const weatherTool = tool(
  async ({ location }: { location: string }) => `Weather in ${location}: Sunny, 72°F`,
  {
    name: "get_weather",
    description: "Get current weather for a location",
    schema: z.object({ location: z.string().describe("City name") }),
  }
);

const agent = createAgent({ model: "gpt-4.1", tools: [searchTool, weatherTool] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in San Francisco?" }],
});
console.log(result.messages[result.messages.length - 1].content);
```
