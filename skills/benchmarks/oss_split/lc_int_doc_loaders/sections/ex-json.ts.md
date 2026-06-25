JSON with JSONPointer extraction:

```typescript
import { JSONLoader } from "langchain/document_loaders/fs/json";

// Load JSON with specific field extraction
const loader = new JSONLoader(
  "path/to/data.json",
  ["/texts/*/content"]  // JSONPointer to extract specific fields
);

const docs = await loader.load();

// Example JSON: { "texts": [{ "content": "...", "id": 1 }] }
// Each matching field becomes a document
```
