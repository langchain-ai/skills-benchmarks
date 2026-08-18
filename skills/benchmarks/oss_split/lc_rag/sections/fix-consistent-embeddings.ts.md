Never mix embedding models between indexing and querying:

Same model for indexing and querying:

```typescript
// BAD: Different embeddings for index and query
const vectorStore = await Chroma.fromDocuments(docs, new OpenAIEmbeddings({ model: "text-embedding-3-small" }));
// Later with different model - incompatible!
const retriever = vectorStore.asRetriever({ embeddings: new OpenAIEmbeddings({ model: "text-embedding-3-large" }) });

// GOOD: Use same embedding model
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorStore = await Chroma.fromDocuments(docs, embeddings);
const retriever = vectorStore.asRetriever();  // Uses same embeddings
```
