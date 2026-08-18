Model calls multiple tools in parallel.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "langchain";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny`,
  {
    name: "get_weather",
    description: "Get weather",
    schema: z.object({ location: z.string() }),
  }
);

const getNews = tool(
  async ({ topic }) => `Latest news about ${topic}`,
  {
    name: "get_news",
    description: "Get news",
    schema: z.object({ topic: z.string() }),
  }
);

const model = new ChatOpenAI({ model: "gpt-4.1" });
const modelWithTools = model.bindTools([getWeather, getNews]);

const response = await modelWithTools.invoke(
  "Get weather for NYC and news about AI"
);

// Model may call both tools in parallel
console.log(response.tool_calls);
// [
//   { name: "get_weather", args: { location: "NYC" }, id: "call_1" },
//   { name: "get_news", args: { topic: "AI" }, id: "call_2" }
// ]
```
