Combine multiple tools in one agent.

```typescript
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";
import { Calculator } from "@langchain/community/tools/calculator";
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { createAgent } from "langchain";

// Define tools
const searchTool = new TavilySearchResults({ maxResults: 3 });
const calculator = new Calculator();

const customTool = tool(
  async ({ query }) => {
    // Your custom logic
    return `Custom result for: ${query}`;
  },
  {
    name: "custom_lookup",
    description: "Look up custom information",
    schema: z.object({
      query: z.string().describe("The query to look up"),
    }),
  }
);

// Create agent with multiple tools
const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool, calculator, customTool],
});

// Agent will choose appropriate tool(s)
const response = await agent.invoke({
  messages: [{
    role: "user",
    content: "Search for the population of Tokyo and calculate if it doubled"
  }]
});
```
