Use splitDocuments for metadata:

```typescript
// Using splitText loses metadata
const chunks = await splitter.splitText(documentText);
// No metadata!

// Use splitDocuments to preserve metadata
const docs = [new Document({
  pageContent: documentText,
  metadata: { source: "file.pdf" }
})];
const chunks = await splitter.splitDocuments(docs);
// Metadata preserved!
```
