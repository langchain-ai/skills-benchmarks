Memory-efficient streaming:

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("large-file.pdf");

// Use lazy() for large files - streams documents
for await (const doc of loader.lazy()) {
  console.log("Processing page:", doc.metadata.loc.pageNumber);
  // Process one page at a time without loading all into memory
}
```
