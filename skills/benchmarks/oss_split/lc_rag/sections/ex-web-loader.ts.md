Load documents from a URL:

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://docs.langchain.com/oss/javascript/langchain/agents");
const docs = await loader.load();
console.log(`Loaded ${docs.length} documents`);
```
