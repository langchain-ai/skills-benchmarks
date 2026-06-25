Chunk long texts before embedding.

```typescript
// Text too long
const embeddings = new OpenAIEmbeddings();
const veryLongText = "...".repeat(100000);
await embeddings.embedQuery(veryLongText); // Will fail!

// Chunk long texts first
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 8000, // OpenAI limit is ~8191 tokens
});
const chunks = await splitter.splitText(veryLongText);
const embeddings = await embeddings.embedDocuments(chunks);
```
