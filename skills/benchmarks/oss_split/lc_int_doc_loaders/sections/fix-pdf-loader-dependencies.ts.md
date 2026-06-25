Install pdf-parse dependency:

```typescript
// Will fail if pdf-parse not installed
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
const loader = new PDFLoader("file.pdf");

// Install dependencies first
// npm install pdf-parse

const loader = new PDFLoader("file.pdf");
const docs = await loader.load(); // Works!
```
