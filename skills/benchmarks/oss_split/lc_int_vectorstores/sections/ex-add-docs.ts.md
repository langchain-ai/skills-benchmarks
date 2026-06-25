Adding documents incrementally to vector store.

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = new MemoryVectorStore(new OpenAIEmbeddings());

// Add documents one at a time or in batches
await vectorStore.addDocuments([
  { pageContent: "Document 1", metadata: {} },
]);

// Add more later
await vectorStore.addDocuments([
  { pageContent: "Document 2", metadata: {} },
  { pageContent: "Document 3", metadata: {} },
]);

// Or from texts
await vectorStore.addTexts(
  ["Text 1", "Text 2"],
  [{ source: "A" }, { source: "B" }]
);
```
