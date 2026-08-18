Filter syntax varies by vector store provider.

```typescript
// Different stores have different filter syntaxes
// Pinecone
const pineconeResults = await pineconeStore.similaritySearch("query", 3, {
  category: "tech" // Simple key-value
});

// Chroma
const chromaResults = await chromaStore.similaritySearch("query", 3, {
  where: { category: "tech" } // Nested structure
});

// Check each store's documentation for filter syntax!
```
