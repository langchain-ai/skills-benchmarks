Bind a tool to a model and inspect the tool_calls returned by the model.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}: Sunny, 72F`,
  { name: "get_weather", description: "Get weather", schema: z.object({ location: z.string() }) }
);

const model = new ChatOpenAI({ model: "gpt-4" });
const modelWithTools = model.bindTools([getWeather]);

const response = await modelWithTools.invoke("What's the weather in SF?");
console.log(response.tool_calls);
// [{ name: 'get_weather', args: { location: 'San Francisco' }, id: 'call_abc123' }]
```
