Similarity search and MMR retrieval:

```typescript
// Similarity search with scores
const results = await vectorStore.similaritySearchWithScore(query, 5);
for (const [doc, score] of results) {
  console.log(`Score: ${score}, Content: ${doc.pageContent}`);
}

// MMR (Maximum Marginal Relevance) for diversity
const retriever = vectorStore.asRetriever({
  searchType: "mmr",
  searchKwargs: { fetchK: 20, lambda: 0.5 },
  k: 5,
});
```
