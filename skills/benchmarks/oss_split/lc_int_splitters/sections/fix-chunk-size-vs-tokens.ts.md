GOOD: Use TokenTextSplitter:

```typescript
// Character count != token count
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 4000,  // Characters
});
// GPT-3.5 has 4096 token limit, this may exceed it!

// Use TokenTextSplitter for precise token counts
import { TokenTextSplitter } from "@langchain/textsplitters";

const splitter = new TokenTextSplitter({
  chunkSize: 4000,  // Actual tokens
  encodingName: "cl100k_base",
});
```
