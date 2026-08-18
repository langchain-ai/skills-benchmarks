Code splitters by language:

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Split code while preserving structure
const jsSplitter = RecursiveCharacterTextSplitter.fromLanguage("js", {
  chunkSize: 500,
  chunkOverlap: 50,
});

const pythonSplitter = RecursiveCharacterTextSplitter.fromLanguage("python", {
  chunkSize: 500,
  chunkOverlap: 50,
});

// Uses language-specific separators (functions, classes, etc.)
```
