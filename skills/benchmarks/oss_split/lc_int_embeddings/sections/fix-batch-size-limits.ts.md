Configure batch size to avoid API limits.

```typescript
// Potential API error with too many docs
const embeddings = new OpenAIEmbeddings();
const hugeDocs = Array(5000).fill("text");
await embeddings.embedDocuments(hugeDocs); // May fail!

// Configure appropriate batch size
const embeddings = new OpenAIEmbeddings({
  batchSize: 512, // OpenAI limit is 2048, use smaller for safety
});
await embeddings.embedDocuments(hugeDocs); // Handles batching automatically
```
