CSV with column config:

```typescript
import { CSVLoader } from "@langchain/community/document_loaders/fs/csv";

const loader = new CSVLoader("path/to/data.csv", {
  column: "text",  // Column to use as page_content
  separator: ",",
});

const docs = await loader.load();

// Each row becomes a document
// Other columns stored in metadata
```
