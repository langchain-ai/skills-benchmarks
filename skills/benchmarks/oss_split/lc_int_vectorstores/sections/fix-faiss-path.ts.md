Use absolute paths for FAISS persistence.

```typescript
// Relative path issues
await vectorStore.save("./index"); // May fail depending on cwd

// Use absolute paths or be explicit
import path from "path";
const indexPath = path.join(process.cwd(), "data", "faiss_index");
await vectorStore.save(indexPath);

// Load with same path
const loadedStore = await FaissStore.load(indexPath, embeddings);
```
