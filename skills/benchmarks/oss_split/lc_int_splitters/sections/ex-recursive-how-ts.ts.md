Custom separator hierarchy:

```typescript
// Tries to split on these separators in order:
// 1. "\n\n" (double newline - paragraphs)
// 2. "\n" (single newline)
// 3. " " (space)
// 4. "" (character-by-character if needed)

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
  separators: ["\n\n", "\n", " ", ""], // Default, can customize
});

// This preserves natural text structure better than simple splitting
```
