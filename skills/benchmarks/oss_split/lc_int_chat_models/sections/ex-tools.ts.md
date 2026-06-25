Define and bind tools with Zod schemas.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";
import { tool } from "@langchain/core/tools";

// Define a tool
const weatherTool = tool(
  async ({ location }) => {
    return `The weather in ${location} is sunny and 72°F`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location",
    schema: z.object({
      location: z.string().describe("The city name"),
    }),
  }
);

// Bind tools to model
const model = new ChatOpenAI({
  modelName: "gpt-4",
}).bindTools([weatherTool]);

const response = await model.invoke("What's the weather in San Francisco?");
console.log(response.tool_calls); // Model will suggest calling the weather tool
```
