Cheerio for static pages:

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

// Load single URL
const loader = new CheerioWebBaseLoader(
  "https://docs.langchain.com"
);

const docs = await loader.load();
console.log(docs[0].pageContent);
console.log(docs[0].metadata); // { source: url, ... }

// With custom selector
const loaderWithSelector = new CheerioWebBaseLoader(
  "https://news.ycombinator.com",
  {
    selector: ".storylink",  // Only extract specific elements
  }
);

// Multiple URLs
const loaderMultiple = new CheerioWebBaseLoader([
  "https://example.com/page1",
  "https://example.com/page2",
]);
const allDocs = await loaderMultiple.load();
```
