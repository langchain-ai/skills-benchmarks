Define researcher subagent with search tool:

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const webSearch = tool(
  async ({ query }) => `Search results for: ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "researcher",
      description: "Conduct web research and compile findings",
      systemPrompt: "Search thoroughly, save to /research/, return summary",
      tools: [webSearch],
    }
  ]
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Research market trends for EVs"
  }]
});
```
