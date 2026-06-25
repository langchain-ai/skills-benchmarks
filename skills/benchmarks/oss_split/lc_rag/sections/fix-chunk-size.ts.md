Too small loses context, too large hits limits. Use 500-1500 characters:

Optimal chunk size configuration:

```typescript
// BAD: Too small - loses context
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 50 });

// BAD: Too large - hits limits
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 10000 });

// GOOD: Balance (500-1500 typically)
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
```
