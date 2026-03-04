---
name: langchain-vector-stores-integration-js
description: "[LangChain] Guide to using vector store integrations in LangChain including Chroma, Pinecone, FAISS, and memory vector stores"
---

<overview>
Vector stores are databases optimized for storing and searching high-dimensional vectors (embeddings). They enable semantic search by finding documents similar to a query based on vector similarity rather than keyword matching. Essential for RAG (Retrieval-Augmented Generation) systems.

Key Concepts:
- **Vector Database**: Specialized database for storing and querying embeddings
- **Similarity Search**: Finding similar documents using vector distance metrics (cosine, euclidean)
- **Metadata Filtering**: Combining vector search with metadata filters
- **Persistence**: Some vector stores run in-memory, others persist to disk/cloud
- **Scaling**: Different stores have different scalability characteristics
</overview>

<vector-store-selection>

| Vector Store | Best For | Package | Persistence | Scalability | Key Features |
|--------------|----------|---------|-------------|-------------|--------------|
| **FAISS** | Local, high performance | `@langchain/community` | Disk | Medium | Fast, CPU/GPU support, local |
| **Chroma** | Development, simplicity | `@langchain/community` | Disk | Medium | Easy setup, local-first, Python API |
| **Pinecone** | Production, managed | `@langchain/pinecone` | Cloud | High | Fully managed, auto-scaling, no ops |
| **Memory** | Testing, prototyping | `langchain/vectorstores/memory` | Memory only | Low | Simple, no setup, ephemeral |
| **Weaviate** | GraphQL, hybrid search | `@langchain/weaviate` | Cloud/Self-hosted | High | GraphQL, hybrid search, modular |
| **Qdrant** | High performance, filtering | `@langchain/qdrant` | Cloud/Self-hosted | High | Fast, advanced filtering, Rust-based |
| **Supabase** | PostgreSQL users | `@langchain/community` | Cloud/Self-hosted | High | PostgreSQL extension, familiar tooling |

</vector-store-selection>

<when-to-use>
**Choose FAISS if:**
- You need high performance local vector search
- You want to avoid external dependencies
- You have many vectors (millions) to search quickly

**Choose Chroma if:**
- You want simple local development
- You need easy persistence without complex setup
- You're building a prototype or small application

**Choose Pinecone if:**
- You're building production applications
- You want zero operational overhead
- You need auto-scaling and high availability

**Choose Memory Vector Store if:**
- You're testing or prototyping
- Data persistence isn't needed
- You want the simplest possible setup

**Choose Weaviate/Qdrant if:**
- You need advanced filtering and hybrid search
- You want flexibility in deployment (cloud or self-hosted)
- You need high performance at scale
</when-to-use>

<ex-memory>
Simple in-memory vector store for testing:

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

// In-memory vector store - great for testing
const vectorStore = new MemoryVectorStore(new OpenAIEmbeddings());

// Add documents
await vectorStore.addDocuments([
  { pageContent: "LangChain is a framework for LLM apps", metadata: { source: "docs" } },
  { pageContent: "Vector stores enable semantic search", metadata: { source: "docs" } },
  { pageContent: "Paris is the capital of France", metadata: { source: "wiki" } },
]);

// Similarity search
const results = await vectorStore.similaritySearch("What is LangChain?", 2);
console.log(results);

// Search with score
const resultsWithScore = await vectorStore.similaritySearchWithScore("LangChain", 2);
resultsWithScore.forEach(([doc, score]) => {
  console.log(`Score: ${score}, Content: ${doc.pageContent}`);
});
```
</ex-memory>

<ex-faiss>
High-performance local vector store:

```typescript
import { FaissStore } from "@langchain/community/vectorstores/faiss";
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Create from documents
const vectorStore = await FaissStore.fromDocuments(
  [
    { pageContent: "Document 1 content", metadata: { id: 1 } },
    { pageContent: "Document 2 content", metadata: { id: 2 } },
  ],
  embeddings
);

// Search
const results = await vectorStore.similaritySearch("query", 3);

// Save to disk
await vectorStore.save("./faiss_index");

// Load from disk
const loadedStore = await FaissStore.load("./faiss_index", embeddings);
```
</ex-faiss>

<ex-chroma>
Local development with persistence:

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

// Requires Chroma server running: docker run -p 8000:8000 chromadb/chroma
const vectorStore = await Chroma.fromDocuments(
  [
    { pageContent: "Text 1", metadata: { category: "A" } },
    { pageContent: "Text 2", metadata: { category: "B" } },
  ],
  new OpenAIEmbeddings(),
  {
    collectionName: "my-collection",
    url: "http://localhost:8000", // Chroma server URL
  }
);

// Search with metadata filter
const results = await vectorStore.similaritySearch("query", 3, {
  category: "A"
});

// Delete collection
await vectorStore.delete({ collectionName: "my-collection" });
```
</ex-chroma>

<ex-pinecone>
Production-ready managed vector store:

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
</ex-pinecone>

<ex-incremental>
Add documents incrementally:

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = new MemoryVectorStore(new OpenAIEmbeddings());

// Add documents one at a time or in batches
await vectorStore.addDocuments([
  { pageContent: "Document 1", metadata: {} },
]);

// Add more later
await vectorStore.addDocuments([
  { pageContent: "Document 2", metadata: {} },
  { pageContent: "Document 3", metadata: {} },
]);

// Or from texts
await vectorStore.addTexts(
  ["Text 1", "Text 2"],
  [{ source: "A" }, { source: "B" }]
);
```
</ex-incremental>

<ex-retriever>
Use vector store as retriever in chains:

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = await MemoryVectorStore.fromDocuments(
  documents,
  new OpenAIEmbeddings()
);

// Convert to retriever
const retriever = vectorStore.asRetriever({
  k: 4, // Return top 4 results
  searchType: "similarity", // or "mmr" for maximum marginal relevance
});

const results = await retriever.invoke("What is LangChain?");
```
</ex-retriever>

<ex-mmr>
Balance relevance and diversity with MMR:

```typescript
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = await MemoryVectorStore.fromTexts(
  ["text1", "text2", "text3"],
  [{}, {}, {}],
  new OpenAIEmbeddings()
);

// MMR balances relevance and diversity
const results = await vectorStore.maxMarginalRelevanceSearch("query", {
  k: 3,
  fetchK: 10, // Fetch 10 candidates, return 3 diverse results
  lambda: 0.5, // 0 = max diversity, 1 = max relevance
});
```
</ex-mmr>

<boundaries>
What Agents CAN Do:
- **Initialize vector stores**: Set up any supported vector store; configure with embeddings and connection details
- **Add and query documents**: Add documents with metadata; perform similarity search; use metadata filters
- **Persist and load**: Save vector stores to disk (FAISS, Chroma); load existing vector stores; manage collections
- **Use as retrievers**: Convert vector stores to retrievers; integrate with chains and agents; configure search parameters (k, filters, etc.)
- **Choose appropriate store**: Select based on scale, performance, persistence needs; switch between stores with minimal code changes

What Agents CANNOT Do:
- **Mix embeddings from different models**: Cannot use different embedding models within same vector store; must use consistent embeddings
- **Bypass provider limits**: Cannot exceed Pinecone index size limits; cannot bypass free tier restrictions
- **Modify vector dimensions after creation**: Cannot change embedding dimensions once store is created; must recreate store with new embeddings
- **Query without proper setup**: Cannot use Chroma without server running; cannot use Pinecone without API key and index
</boundaries>

<fix-embedding-consistency>
Use same embedding model for all operations:

```typescript
// BAD: Different embeddings for indexing and querying
const store1 = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings({ model: "text-embedding-3-small" })
);

// But if you recreate with different model:
const store2 = new MemoryVectorStore(
  new OpenAIEmbeddings({ model: "text-embedding-ada-002" }) // Different!
);
// Queries won't work correctly!

// GOOD: Keep embedding instance
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = await MemoryVectorStore.fromDocuments(docs, embeddings);
// Always use same embeddings instance
```
</fix-embedding-consistency>

<fix-chroma-server>
Ensure Chroma server is running:

```typescript
// Chroma not running - will fail
import { Chroma } from "@langchain/community/vectorstores/chroma";

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
});
// Error: Connection refused!

// Fix: Start Chroma first
// Terminal: docker run -p 8000:8000 chromadb/chroma
// Or: chroma run --path ./chroma_data

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
}); // Works!
```
</fix-chroma-server>

<fix-pinecone-index>
Create Pinecone index before using:

```typescript
// Index doesn't exist - will fail
import { Pinecone } from "@pinecone-database/pinecone";

const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
const index = pinecone.Index("nonexistent-index"); // Won't create index!

// Fix: Create index first
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
</fix-pinecone-index>

<fix-faiss-paths>
Use absolute paths for FAISS save/load:

```typescript
// Relative path issues
await vectorStore.save("./index"); // May fail depending on cwd

// Fix: Use absolute paths or be explicit
import path from "path";
const indexPath = path.join(process.cwd(), "data", "faiss_index");
await vectorStore.save(indexPath);

// Load with same path
const loadedStore = await FaissStore.load(indexPath, embeddings);
```
</fix-faiss-paths>

<fix-memory-ephemeral>
Use persistent store for production:

```typescript
// Problem: Expecting persistence from MemoryVectorStore
const vectorStore = new MemoryVectorStore(embeddings);
await vectorStore.addDocuments(docs);
// App restarts...
// All data is lost!

// Fix: Use persistent store for production
import { FaissStore } from "@langchain/community/vectorstores/faiss";

const vectorStore = await FaissStore.fromDocuments(docs, embeddings);
await vectorStore.save("./faiss_index"); // Persists to disk
```
</fix-memory-ephemeral>

<fix-filter-syntax>
Different stores have different filter syntaxes:

```typescript
// Different stores have different filter syntaxes
// Pinecone
const pineconeResults = await pineconeStore.similaritySearch("query", 3, {
  category: "tech" // Simple key-value
});

// Chroma
const chromaResults = await chromaStore.similaritySearch("query", 3, {
  where: { category: "tech" } // Nested structure
});

// Check each store's documentation for filter syntax!
```
</fix-filter-syntax>

<fix-dimension-mismatch>
Match embedding dimensions to index:

```typescript
// Creating Pinecone index with wrong dimensions
await pinecone.createIndex({
  name: "my-index",
  dimension: 1536, // OpenAI ada-002 dimensions
});

// But using different embeddings!
const store = await PineconeStore.fromDocuments(
  docs,
  new OpenAIEmbeddings({ model: "text-embedding-3-small", dimensions: 512 }),
  { pineconeIndex }
); // Error: dimension mismatch!

// Fix: Match dimensions
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
// Default is 1536, matches Pinecone index
```
</fix-dimension-mismatch>

<documentation-links>
Official Documentation:
- [LangChain JS Vector Stores](https://js.langchain.com/docs/integrations/vectorstores/)
- [FAISS](https://js.langchain.com/docs/integrations/vectorstores/faiss)
- [Chroma](https://js.langchain.com/docs/integrations/vectorstores/chroma)
- [Pinecone](https://js.langchain.com/docs/integrations/vectorstores/pinecone)
- [Memory Vector Store](https://js.langchain.com/docs/integrations/vectorstores/memory)

Provider Documentation:
- [FAISS Library](https://github.com/facebookresearch/faiss)
- [Chroma](https://docs.trychroma.com/)
- [Pinecone](https://docs.pinecone.io/)
- [Weaviate](https://weaviate.io/developers/weaviate)
- [Qdrant](https://qdrant.tech/documentation/)

Package Installation:
```bash
# Community package (includes FAISS, Chroma, etc.)
npm install @langchain/community

# Pinecone
npm install @langchain/pinecone @pinecone-database/pinecone

# Weaviate
npm install @langchain/weaviate weaviate-ts-client

# Qdrant
npm install @langchain/qdrant @qdrant/js-client-rest
```
</documentation-links>
