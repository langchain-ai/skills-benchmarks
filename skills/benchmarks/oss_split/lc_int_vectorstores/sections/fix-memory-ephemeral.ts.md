Memory stores are ephemeral, use FAISS instead.

```typescript
// Expecting persistence
const vectorStore = new MemoryVectorStore(embeddings);
await vectorStore.addDocuments(docs);
// App restarts...
// All data is lost!

// Use persistent store for production
import { FaissStore } from "@langchain/community/vectorstores/faiss";

const vectorStore = await FaissStore.fromDocuments(docs, embeddings);
await vectorStore.save("./faiss_index"); // Persists to disk
```
