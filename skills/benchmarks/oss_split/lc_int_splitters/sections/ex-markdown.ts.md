Markdown structure-aware splitting:

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// Split markdown while preserving structure
const splitter = RecursiveCharacterTextSplitter.fromLanguage("markdown", {
  chunkSize: 1000,
  chunkOverlap: 200,
});

const markdown = `
# Header 1

Some content under header 1.

## Header 2

Content under header 2.
`;

const chunks = await splitter.splitText(markdown);
// Tries to keep headers with their content
```
