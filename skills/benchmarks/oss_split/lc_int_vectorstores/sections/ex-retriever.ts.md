Vector store as retriever.

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = await MemoryVectorStore.fromDocuments(
  documents,
  new OpenAIEmbeddings()
);

// Convert to retriever
const retriever = vectorStore.asRetriever({
  k: 4, // Return top 4 results
  searchType: "similarity", // or "mmr" for maximum marginal relevance
});

const results = await retriever.invoke("What is LangChain?");
```
