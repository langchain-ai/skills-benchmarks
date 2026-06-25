Fetch and parse content from a web URL into a document using Cheerio.
```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://docs.langchain.com");
const docs = await loader.load();
```
