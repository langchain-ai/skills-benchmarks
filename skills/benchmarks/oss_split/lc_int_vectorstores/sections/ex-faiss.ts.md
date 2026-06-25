FAISS vector store with persistence.

```typescript
import { FaissStore } from "@langchain/community/vectorstores/faiss";
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Create from documents
const vectorStore = await FaissStore.fromDocuments(
  [
    { pageContent: "Document 1 content", metadata: { id: 1 } },
    { pageContent: "Document 2 content", metadata: { id: 2 } },
  ],
  embeddings
);

// Search
const results = await vectorStore.similaritySearch("query", 3);

// Save to disk
await vectorStore.save("./faiss_index");

// Load from disk
const loadedStore = await FaissStore.load("./faiss_index", embeddings);
```
