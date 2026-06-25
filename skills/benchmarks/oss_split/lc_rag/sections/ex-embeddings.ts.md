Configure embedding models:

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

// Different embedding models
const smallEmbeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });  // 1536 dim
const largeEmbeddings = new OpenAIEmbeddings({ model: "text-embedding-3-large" });  // 3072 dim

// Custom dimensions (for 3rd gen models)
const customEmbeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-large",
  dimensions: 1024,  // Reduce from 3072 to save space
});
```
