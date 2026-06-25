Define subagent with custom tools:

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const searchPapers = tool(
  async ({ query }) => `Found 10 papers about ${query}`,
  {
    name: "search_papers",
    description: "Search academic papers",
    schema: z.object({ query: z.string() }),
  }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "research",
      description: "Research academic papers and provide summaries",
      systemPrompt: "You are a research assistant. Provide concise summaries.",
      tools: [searchPapers],
      model: "claude-sonnet-4-5-20250929",  // Optional
    }
  ]
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Research recent papers on transformers" }]
});
```
