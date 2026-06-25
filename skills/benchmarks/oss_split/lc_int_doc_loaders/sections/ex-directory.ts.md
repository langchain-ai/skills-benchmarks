Multi-format directory loader:

```typescript
import { DirectoryLoader } from "langchain/document_loaders/fs/directory";
import { TextLoader } from "langchain/document_loaders/fs/text";
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

// Load all files from directory
const loader = new DirectoryLoader(
  "path/to/documents",
  {
    ".txt": (path) => new TextLoader(path),
    ".pdf": (path) => new PDFLoader(path),
  }
);

const docs = await loader.load();
console.log(`Loaded ${docs.length} documents from directory`);
```
