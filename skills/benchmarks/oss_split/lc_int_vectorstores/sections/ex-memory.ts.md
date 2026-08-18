In-memory vector store with similarity search.

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

// In-memory vector store - great for testing
const vectorStore = new MemoryVectorStore(new OpenAIEmbeddings());

// Add documents
await vectorStore.addDocuments([
  { pageContent: "LangChain is a framework for LLM apps", metadata: { source: "docs" } },
  { pageContent: "Vector stores enable semantic search", metadata: { source: "docs" } },
  { pageContent: "Paris is the capital of France", metadata: { source: "wiki" } },
]);

// Similarity search
const results = await vectorStore.similaritySearch("What is LangChain?", 2);
console.log(results);

// Search with score
const resultsWithScore = await vectorStore.similaritySearchWithScore("LangChain", 2);
resultsWithScore.forEach(([doc, score]) => {
  console.log(`Score: ${score}, Content: ${doc.pageContent}`);
});
```
