Split PDF with metadata:

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load PDF
const loader = new PDFLoader("large-document.pdf");
const docs = await loader.load();

// Split into manageable chunks
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});

const splitDocs = await splitter.splitDocuments(docs);

console.log(`${docs.length} pages split into ${splitDocs.length} chunks`);

// Each chunk preserves source metadata
splitDocs.forEach(chunk => {
  console.log(chunk.metadata); // Includes original page number
});
```
