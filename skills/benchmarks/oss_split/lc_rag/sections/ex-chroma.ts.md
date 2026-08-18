Persistent vector store with Chroma:

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Create and populate
const vectorStore = await Chroma.fromDocuments(splits, embeddings, { collectionName: "my-docs" });

// Later: Load existing
const vectorStore2 = await Chroma.fromExistingCollection(embeddings, { collectionName: "my-docs" });
```
