BAD vs GOOD chunk sizes:

```typescript
// Chunks too small
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 100,    // Very small
  chunkOverlap: 0,   // No overlap
});
// Chunks lack sufficient context for good retrieval

// Reasonable chunk size with overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,   // Good size
  chunkOverlap: 200, // 20% overlap
});
```
