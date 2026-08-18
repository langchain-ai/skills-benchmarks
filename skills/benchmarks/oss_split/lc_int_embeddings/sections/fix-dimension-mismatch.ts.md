Ensure consistent embedding dimensions.

```typescript
// Vector store expecting 1536 dimensions, model produces 512
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  dimensions: 512,
});

// Vector store created with default 1536 dimensions
const vectorStore = await MemoryVectorStore.fromTexts(
  ["text1"],
  embeddings, // Mismatch!
);

// Consistent dimensions
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  // Don't override dimensions, or ensure vector store matches
});
```
