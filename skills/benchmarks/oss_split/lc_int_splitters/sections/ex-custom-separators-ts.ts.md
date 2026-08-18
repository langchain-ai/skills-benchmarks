Custom separator precedence:

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Custom splitting logic
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 100,
  separators: [
    "\n\n\n",  // Triple newline (section breaks)
    "\n\n",    // Double newline (paragraphs)
    "\n",      // Single newline
    ". ",      // Sentences
    " ",       // Words
    "",        // Characters
  ],
});
```
