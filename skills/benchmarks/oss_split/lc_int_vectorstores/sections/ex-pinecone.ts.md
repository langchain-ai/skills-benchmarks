Pinecone managed cloud vector store.

```typescript
import { PineconeStore } from "@langchain/pinecone";
import { Pinecone } from "@pinecone-database/pinecone";
import { OpenAIEmbeddings } from "@langchain/openai";

// Initialize Pinecone client
const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY,
});

const pineconeIndex = pinecone.Index("my-index");

// Create vector store
const vectorStore = await PineconeStore.fromDocuments(
  [
    { pageContent: "Content 1", metadata: { topic: "tech" } },
    { pageContent: "Content 2", metadata: { topic: "science" } },
  ],
  new OpenAIEmbeddings(),
  {
    pineconeIndex,
    maxConcurrency: 5,
  }
);

// Search with metadata filter
const results = await vectorStore.similaritySearch("query", 3, {
  topic: "tech"
});

// Use as retriever
const retriever = vectorStore.asRetriever({
  k: 5,
  searchType: "similarity",
});
const docs = await retriever.getRelevantDocuments("query");
```
