Load a PDF file and extract each page as a separate document.
```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("./document.pdf");
const docs = await loader.load();
console.log(`Loaded ${docs.length} pages`);
```
