Query Wikipedia for encyclopedic information.

```typescript
import { WikipediaQueryRun } from "@langchain/community/tools/wikipedia_query_run";

const wikipediaTool = new WikipediaQueryRun({
  topKResults: 3,
  maxDocContentLength: 4000,
});

// Query Wikipedia
const result = await wikipediaTool.invoke("Artificial Intelligence");
console.log(result);
```
