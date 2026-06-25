PDF with page metadata:

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load PDF file
const loader = new PDFLoader("path/to/document.pdf");
const docs = await loader.load();

console.log(`Loaded ${docs.length} pages`);
docs.forEach((doc, i) => {
  console.log(`Page ${i + 1}:`, doc.metadata);
  console.log(doc.pageContent.substring(0, 100));
});

// Each page is a separate document
// metadata includes: source, pdf.totalPages, loc.pageNumber
```
