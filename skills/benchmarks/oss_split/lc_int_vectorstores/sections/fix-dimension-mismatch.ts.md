Match embedding dimensions to index dimensions.

```typescript
// Creating Pinecone index with wrong dimensions
await pinecone.createIndex({
  name: "my-index",
  dimension: 1536, // OpenAI ada-002 dimensions
});

// But using different embeddings!
const store = await PineconeStore.fromDocuments(
  docs,
  new OpenAIEmbeddings({ model: "text-embedding-3-small", dimensions: 512 }),
  { pineconeIndex }
); // Error: dimension mismatch!

// Match dimensions
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
// Default is 1536, matches Pinecone index
```
