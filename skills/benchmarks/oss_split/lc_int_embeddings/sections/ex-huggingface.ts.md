Run local HuggingFace embeddings.

```typescript
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/hf_transformers";

// Run embeddings locally with Transformers.js
const embeddings = new HuggingFaceTransformersEmbeddings({
  modelName: "Xenova/all-MiniLM-L6-v2",
});

const embedding = await embeddings.embedQuery("This runs locally!");
```
