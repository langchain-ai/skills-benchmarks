Chunk size 500-1500 is typically good.
```typescript
// WRONG: Too small or too large
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 50 });

// CORRECT
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
```
