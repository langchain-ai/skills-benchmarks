Initialize Tavily search and use with agent.

```typescript
import { TavilySearchResults } from "@langchain/community/tools/tavily_search";

// Initialize Tavily (requires API key)
const searchTool = new TavilySearchResults({
  maxResults: 3,
  apiKey: process.env.TAVILY_API_KEY,
});

// Use directly
const results = await searchTool.invoke("Latest AI news");
console.log(results);

// Use with agent
import { createAgent } from "langchain";

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchTool],
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "What's new in AI today?" }]
});
```
