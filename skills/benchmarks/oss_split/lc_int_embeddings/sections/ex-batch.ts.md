Batch process large document sets efficiently.

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings({
  batchSize: 512, // OpenAI allows up to 2048 in one request
});

// Efficiently embed large document sets
const largeDocSet = Array.from({ length: 1000 }, (_, i) =>
  `Document ${i}: Some content here`
);

const docEmbeddings = await embeddings.embedDocuments(largeDocSet);
console.log(`Embedded ${docEmbeddings.length} documents in batches`);
```
