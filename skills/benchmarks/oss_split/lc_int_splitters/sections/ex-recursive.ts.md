Recursive splitter with metadata:

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Basic usage
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,      // Target chunk size in characters
  chunkOverlap: 200,    // Overlap between chunks
});

const text = "Long document text here...";
const chunks = await splitter.splitText(text);

console.log(`Created ${chunks.length} chunks`);
chunks.forEach((chunk, i) => {
  console.log(`Chunk ${i + 1}: ${chunk.length} characters`);
});

// Split documents (preserves metadata)
import { Document } from "@langchain/core/documents";

const docs = [
  new Document({
    pageContent: "Long text...",
    metadata: { source: "doc1.pdf", page: 1 }
  })
];

const splitDocs = await splitter.splitDocuments(docs);
// Metadata is preserved and enriched with loc.lines
```
