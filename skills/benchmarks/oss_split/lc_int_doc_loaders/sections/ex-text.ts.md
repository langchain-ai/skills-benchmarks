Text file with metadata:

```typescript
import { TextLoader } from "langchain/document_loaders/fs/text";

const loader = new TextLoader("path/to/file.txt");
const docs = await loader.load();

// Returns single document with entire file content
console.log(docs[0].pageContent);
console.log(docs[0].metadata.source); // File path
```
