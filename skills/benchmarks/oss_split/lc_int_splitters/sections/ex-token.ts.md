Precise token counting:

```typescript
import { TokenTextSplitter } from "@langchain/textsplitters";

// Split based on actual token count
const splitter = new TokenTextSplitter({
  chunkSize: 512,       // Number of tokens, not characters
  chunkOverlap: 50,
  encodingName: "cl100k_base", // OpenAI's encoding
});

const chunks = await splitter.splitText(text);

// Good for precise model context window management
// 1 token ~ 4 characters for English text, but varies
```
