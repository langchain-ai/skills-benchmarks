Use persistent vector store instead of in-memory to avoid data loss.
```typescript
// WRONG: Memory - lost on restart
const vectorstore = await MemoryVectorStore.fromDocuments(docs, embeddings);

// CORRECT
const vectorstore = await Chroma.fromDocuments(docs, embeddings, { collectionName: "my-collection" });
```
