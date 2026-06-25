Create a basic React agent with a search tool and invoke it with a user message.
```typescript
import { createAgent } from "langchain";
import { ChatOpenAI } from "@langchain/openai";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => `Results for: ${query}`,
  { name: "search", description: "Search for information", schema: z.object({ query: z.string() }) }
);

const agent = createAgent({ model: "gpt-4.1", tools: [search] });

const result = await agent.invoke({
  messages: [{ role: "user", content: "Search for AI news" }]
});
console.log(result.messages.at(-1).content);
```
