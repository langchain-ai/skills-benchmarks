Combine keyword and vector search:

```typescript
// Combine keyword and vector search
async function hybridSearch(query: string, k: number = 5) {
  // Vector search
  const vectorResults = await vectorStore.similaritySearch(query, k);

  // Keyword search (simple example)
  const allDocs = await vectorStore.getAllDocuments();
  const keywordResults = allDocs.filter(doc =>
    doc.pageContent.toLowerCase().includes(query.toLowerCase())
  );

  // Combine and deduplicate
  const combined = [...vectorResults, ...keywordResults];
  const unique = Array.from(new Set(combined.map(d => d.pageContent)))
    .map(content => combined.find(d => d.pageContent === content));

  return unique.slice(0, k);
}
```
