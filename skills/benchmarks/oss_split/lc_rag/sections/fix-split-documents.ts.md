Large documents exceed embedding limits. Always split first:

Split before adding to vector store:

```typescript
// BAD: Entire documents are too large
await vectorStore.addDocuments(largeDocs);

// GOOD: Always split first
const splits = await splitter.splitDocuments(largeDocs);
await vectorStore.addDocuments(splits);
```
