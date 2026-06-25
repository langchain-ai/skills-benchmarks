Create and invoke a basic agent with tools using createAgent.
```typescript
import { createAgent } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => `Results for: ${query}`,
  {
    name: "search",
    description: "Search for information on the web.",
    schema: z.object({ query: z.string().describe("The search query") }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  systemPrompt: "You are a helpful assistant.",
});

const result = await agent.invoke({ messages: [["user", "Search for LangChain docs"]] });
```
