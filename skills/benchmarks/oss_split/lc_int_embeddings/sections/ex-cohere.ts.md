Use Cohere embeddings for multilingual support.

```typescript
import { CohereEmbeddings } from "@langchain/cohere";

const embeddings = new CohereEmbeddings({
  apiKey: process.env.COHERE_API_KEY,
  model: "embed-english-v3.0",
  inputType: "search_query", // or "search_document", "classification", "clustering"
});

const queryEmbedding = await embeddings.embedQuery("Search query");
const docEmbeddings = await embeddings.embedDocuments(["doc1", "doc2"]);
```
