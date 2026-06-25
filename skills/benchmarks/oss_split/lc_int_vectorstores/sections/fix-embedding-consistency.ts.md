Keep embedding models consistent across operations.

```typescript
// BAD: Different embeddings for indexing and querying
const store1 = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings({ model: "text-embedding-3-small" })
);

const results = await store1.similaritySearch("query"); // Uses same embeddings

// But if you recreate:
const store2 = new MemoryVectorStore(
  new OpenAIEmbeddings({ model: "text-embedding-ada-002" }) // Different!
);
// Queries won't work correctly!

// GOOD: Keep embedding instance
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = await MemoryVectorStore.fromDocuments(docs, embeddings);
// Always use same embeddings instance
```
