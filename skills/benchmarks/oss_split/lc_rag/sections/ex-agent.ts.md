RAG-enabled agent with retriever tool:

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const searchDocs = tool(
  async ({ query }) => {
    const docs = await retriever.invoke(query);
    return docs.map(d => d.pageContent).join("\n\n");
  },
  {
    name: "search_docs",
    description: "Search documentation for relevant information",
    schema: z.object({ query: z.string().describe("Search query") }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchDocs],
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "How do I create an agent?" }],
});
```
