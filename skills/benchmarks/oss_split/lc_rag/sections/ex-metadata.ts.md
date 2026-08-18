Filter search by metadata:

```typescript
const docs = [
  { pageContent: "Python programming guide", metadata: { language: "python", topic: "programming" } },
  { pageContent: "JavaScript tutorial", metadata: { language: "javascript", topic: "programming" } },
];

// Search with filter
const results = await vectorStore.similaritySearch("programming", 5, { language: "python" });
```
