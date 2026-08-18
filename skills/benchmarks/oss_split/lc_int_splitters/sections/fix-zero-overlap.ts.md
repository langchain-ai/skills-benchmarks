Add overlap for context:

```typescript
// No overlap
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 0,  // Information at boundaries may be lost
});

// Use overlap to preserve context
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,  // 20% overlap is good default
});
```
