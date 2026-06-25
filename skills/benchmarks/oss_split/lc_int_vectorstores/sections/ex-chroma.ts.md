Chroma with server connection and filtering.

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

// Requires Chroma server running: docker run -p 8000:8000 chromadb/chroma
const vectorStore = await Chroma.fromDocuments(
  [
    { pageContent: "Text 1", metadata: { category: "A" } },
    { pageContent: "Text 2", metadata: { category: "B" } },
  ],
  new OpenAIEmbeddings(),
  {
    collectionName: "my-collection",
    url: "http://localhost:8000", // Chroma server URL
  }
);

// Search with metadata filter
const results = await vectorStore.similaritySearch("query", 3, {
  category: "A"
});

// Delete collection
await vectorStore.delete({ collectionName: "my-collection" });
```
