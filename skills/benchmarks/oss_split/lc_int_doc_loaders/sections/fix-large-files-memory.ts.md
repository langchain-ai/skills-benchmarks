Stream instead of load all:

```typescript
// Loading huge PDF into memory
const loader = new PDFLoader("huge-book.pdf");
const docs = await loader.load(); // May crash!

// Use lazy loading
for await (const doc of loader.lazy()) {
  processDocument(doc);
  // Only one page in memory at a time
}
```
