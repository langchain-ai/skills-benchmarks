Use consistent models across all embeddings.

```typescript
// BAD: Using different models
const embeddings1 = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const embeddings2 = new OpenAIEmbeddings({
  modelName: "text-embedding-ada-002"
});

const queryVec = await embeddings1.embedQuery("query");
const docVec = await embeddings2.embedQuery("document");
// Similarity comparison will be meaningless!

// GOOD: Use same model for everything
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const queryVec = await embeddings.embedQuery("query");
const docVec = await embeddings.embedQuery("document");
// Now similarity makes sense
```
