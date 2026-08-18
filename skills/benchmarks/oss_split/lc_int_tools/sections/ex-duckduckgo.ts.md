Search web without API key using DuckDuckGo.

```typescript
import { DuckDuckGoSearch } from "@langchain/community/tools/duckduckgo_search";

const searchTool = new DuckDuckGoSearch({
  maxResults: 5,
});

const results = await searchTool.invoke("LangChain framework");
```
