Add timestamp and category:

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://blog.com/post");
const docs = await loader.load();

// Add custom metadata
const enrichedDocs = docs.map(doc => ({
  ...doc,
  metadata: {
    ...doc.metadata,
    loadedAt: new Date().toISOString(),
    category: "blog",
  },
}));
```
