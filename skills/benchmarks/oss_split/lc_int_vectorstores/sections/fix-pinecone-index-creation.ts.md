Create Pinecone index before using it.

```typescript
// Index doesn't exist
import { Pinecone } from "@pinecone-database/pinecone";

const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
const index = pinecone.Index("nonexistent-index"); // Won't create index!

// Create index first
const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });

// Check if index exists, create if needed
const indexList = await pinecone.listIndexes();
if (!indexList.indexes?.some(idx => idx.name === "my-index")) {
  await pinecone.createIndex({
    name: "my-index",
    dimension: 1536, // Must match embedding dimensions
    metric: "cosine",
    spec: { serverless: { cloud: "aws", region: "us-east-1" } }
  });
}

const index = pinecone.Index("my-index");
```
