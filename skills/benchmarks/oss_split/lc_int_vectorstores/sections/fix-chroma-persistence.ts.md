Start Chroma server before connecting.

```typescript
// Chroma not running
import { Chroma } from "@langchain/community/vectorstores/chroma";

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
});
// Error: Connection refused!

// Start Chroma first
// Terminal: docker run -p 8000:8000 chromadb/chroma
// Or: chroma run --path ./chroma_data

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
}); // Works!
```
