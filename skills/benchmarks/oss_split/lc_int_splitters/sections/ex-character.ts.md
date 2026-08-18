Split by paragraph breaks:

```typescript
import { CharacterTextSplitter } from "@langchain/textsplitters";

// Split by single separator
const splitter = new CharacterTextSplitter({
  separator: "\n\n",    // Split on double newlines
  chunkSize: 1000,
  chunkOverlap: 200,
});

const chunks = await splitter.splitText(text);
```
