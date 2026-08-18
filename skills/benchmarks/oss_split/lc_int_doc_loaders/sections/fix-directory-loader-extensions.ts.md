Include dot in extensions:

```typescript
// Extensions don't match
const loader = new DirectoryLoader("docs", {
  "txt": (path) => new TextLoader(path),  // Wrong!
});

// Include the dot
const loader = new DirectoryLoader("docs", {
  ".txt": (path) => new TextLoader(path),
  ".pdf": (path) => new PDFLoader(path),
});
```
