Maximum marginal relevance for diverse results.

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = await MemoryVectorStore.fromTexts(
  ["text1", "text2", "text3"],
  [{}, {}, {}],
  new OpenAIEmbeddings()
);

// MMR balances relevance and diversity
const results = await vectorStore.maxMarginalRelevanceSearch("query", {
  k: 3,
  fetchK: 10, // Fetch 10 candidates, return 3 diverse results
  lambda: 0.5, // 0 = max diversity, 1 = max relevance
});
```
