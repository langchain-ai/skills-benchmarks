---
name: LangChain Vector Stores Integration
description: "[LangChain] Guide to using vector store integrations in LangChain including Chroma, Pinecone, FAISS, and memory vector stores"
---

<oneliner>
Vector stores are databases optimized for storing and searching high-dimensional vectors (embeddings), enabling semantic search and RAG systems.
</oneliner>

<overview>
Key Concepts:
- **Vector Database**: Specialized database for storing and querying embeddings
- **Similarity Search**: Finding similar documents using vector distance metrics (cosine, euclidean)
- **Metadata Filtering**: Combining vector search with metadata filters
- **Persistence**: Some vector stores run in-memory, others persist to disk/cloud
- **Scaling**: Different stores have different scalability characteristics
</overview>

<vector-store-selection>
| Vector Store | Best For | Package (Python / TypeScript) | Persistence | Scalability | Key Features |
|--------------|----------|-------------------------------|-------------|-------------|--------------|
| **FAISS** | Local, high performance | `langchain-community` / `@langchain/community` | Disk | Medium | Fast, CPU/GPU support, local |
| **Chroma** | Development, simplicity | `langchain-chroma` / `@langchain/community` | Disk | Medium | Easy setup, local-first |
| **Pinecone** | Production, managed | `langchain-pinecone` / `@langchain/pinecone` | Cloud | High | Fully managed, auto-scaling |
| **InMemory/Memory** | Testing, prototyping | `langchain-core` / `langchain/vectorstores/memory` | Memory only | Low | Simple, no setup, ephemeral |
| **Weaviate** | GraphQL, hybrid search | `langchain-weaviate` / `@langchain/weaviate` | Cloud/Self-hosted | High | GraphQL, hybrid search |
| **Qdrant** | High performance, filtering | `langchain-qdrant` / `@langchain/qdrant` | Cloud/Self-hosted | High | Fast, advanced filtering |
| **PGVector/Supabase** | PostgreSQL users | `langchain-postgres` / `@langchain/community` | PostgreSQL | High | PostgreSQL extension |
</vector-store-selection>

<when-to-choose-store>
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

**Choose InMemory/Memory Vector Store if:**
- You're testing or prototyping
- Data persistence isn't needed
- You want the simplest possible setup

**Choose Weaviate/Qdrant if:**
- You need advanced filtering and hybrid search
- You want flexibility in deployment (cloud or self-hosted)
- You need high performance at scale
</when-to-choose-store>

<ex-memory>
<python>

In-memory vector store with similarity search.

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# In-memory vector store - great for testing
vectorstore = InMemoryVectorStore(OpenAIEmbeddings())

# Add documents
from langchain_core.documents import Document

docs = [
    Document(page_content="LangChain is a framework for LLM apps", metadata={"source": "docs"}),
    Document(page_content="Vector stores enable semantic search", metadata={"source": "docs"}),
    Document(page_content="Paris is the capital of France", metadata={"source": "wiki"}),
]
vectorstore.add_documents(docs)

# Similarity search
results = vectorstore.similarity_search("What is LangChain?", k=2)
for doc in results:
    print(doc.page_content)

# Search with score
results_with_score = vectorstore.similarity_search_with_score("LangChain", k=2)
for doc, score in results_with_score:
    print(f"Score: {score}, Content: {doc.page_content}")
```

</python>

<typescript>

In-memory vector store with similarity search.

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

</typescript>
</ex-memory>

<ex-faiss>
<python>

FAISS vector store with persistence.

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import faiss

embeddings = OpenAIEmbeddings()

# Create from documents
docs = [
    Document(page_content="Document 1 content", metadata={"id": 1}),
    Document(page_content="Document 2 content", metadata={"id": 2}),
]
vectorstore = FAISS.from_documents(docs, embeddings)

# Search
results = vectorstore.similarity_search("query", k=3)

# Save to disk
vectorstore.save_local("./faiss_index")

# Load from disk
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True  # Required for loading
)

# Alternative: Initialize with specific FAISS index
embedding_dim = len(embeddings.embed_query("test"))
index = faiss.IndexFlatL2(embedding_dim)
docstore = InMemoryDocstore()
vectorstore = FAISS(embeddings, index, docstore, {})
```

</python>

<typescript>

FAISS vector store with persistence.

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

</typescript>
</ex-faiss>

<ex-chroma>
<python>

Chroma with persistence and metadata filtering.

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Persistent Chroma (saves to disk)
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db",
    collection_name="my-collection",
)

# Search with metadata filter
results = vectorstore.similarity_search(
    "query",
    k=3,
    filter={"category": "A"}
)

# Load existing collection
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(),
    collection_name="my-collection",
)

# Delete collection
vectorstore.delete_collection()
```

</python>

<typescript>

Chroma with server connection and filtering.

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

</typescript>
</ex-chroma>

<ex-pinecone>
<python>

Pinecone managed cloud vector store.

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
import os

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index if it doesn't exist
index_name = "my-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embedding dimensions
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Create vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index=index,
)

# Search with metadata filter
results = vectorstore.similarity_search(
    "query",
    k=3,
    filter={"topic": "tech"}
)

# Use as retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
docs = retriever.get_relevant_documents("query")
```

</python>

<typescript>

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

</typescript>
</ex-pinecone>

<ex-add-docs>
<python>

Adding documents incrementally to vector store.

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = InMemoryVectorStore(OpenAIEmbeddings())

# Add documents
vectorstore.add_documents([
    Document(page_content="Document 1", metadata={}),
])

# Add more later
vectorstore.add_documents([
    Document(page_content="Document 2", metadata={}),
    Document(page_content="Document 3", metadata={}),
])

# Or from texts
vectorstore.add_texts(
    texts=["Text 1", "Text 2"],
    metadatas=[{"source": "A"}, {"source": "B"}]
)
```

</python>

<typescript>

Adding documents incrementally to vector store.

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

</typescript>
</ex-add-docs>

<ex-retriever>
<python>

Vector store as retriever in RAG chain.

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# Create vector store
vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())

# Convert to retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",  # or "mmr"
    search_kwargs={"k": 4}
)

# Use in a chain
llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("""
Answer based on context:
{context}

Question: {input}
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

result = retrieval_chain.invoke({"input": "What is LangChain?"})
print(result["answer"])
```

</python>

<typescript>

Vector store as retriever in RAG chain.

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

// Use in a chain
import { ChatOpenAI } from "@langchain/openai";
import { createRetrievalChain } from "langchain/chains/retrieval";
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const llm = new ChatOpenAI();
const prompt = ChatPromptTemplate.fromTemplate(`
Answer based on context:
{context}

Question: {input}
`);

const combineDocsChain = await createStuffDocumentsChain({ llm, prompt });
const chain = await createRetrievalChain({
  retriever,
  combineDocsChain,
});

const result = await chain.invoke({ input: "What is LangChain?" });
```

</typescript>
</ex-retriever>

<ex-mmr>
<python>

Maximum marginal relevance for diverse results.

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = InMemoryVectorStore.from_texts(
    texts=["text1", "text2", "text3"],
    metadatas=[{}, {}, {}],
    embedding=OpenAIEmbeddings()
)

# MMR balances relevance and diversity
results = vectorstore.max_marginal_relevance_search(
    "query",
    k=3,
    fetch_k=10,  # Fetch 10 candidates, return 3 diverse results
    lambda_mult=0.5  # 0 = max diversity, 1 = max relevance
)
```

</python>

<typescript>

Maximum marginal relevance for diverse results.

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

</typescript>
</ex-mmr>

<boundaries>
What You CAN Do:
- **Initialize vector stores** - Set up any supported vector store, configure with embeddings and connection details
- **Add and query documents** - Add documents with metadata, perform similarity search, use metadata filters
- **Persist and load** - Save vector stores to disk (FAISS, Chroma), load existing vector stores, manage collections
- **Use as retrievers** - Convert vector stores to retrievers, integrate with chains and agents, configure search parameters
- **Choose appropriate store** - Select based on scale, performance, persistence needs; switch between stores with minimal code changes

What You CANNOT Do:
- **Mix embeddings from different models** - Cannot use different embedding models within same vector store; must use consistent embeddings
- **Bypass provider limits** - Cannot exceed Pinecone index size limits or bypass free tier restrictions
- **Modify vector dimensions after creation** - Cannot change embedding dimensions once store is created; must recreate store with new embeddings
- **Query without proper setup** - Cannot use Chroma without server running (TypeScript), cannot use Pinecone without API key and index
</boundaries>

<fix-faiss-deserialize>
<python>

Fix FAISS deserialization security error.

```python
# Will raise error
loaded_store = FAISS.load_local("./faiss_index", embeddings)

# Must explicitly allow deserialization
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
```
</python>
</fix-faiss-deserialize>

<fix-import-packages>
<python>

Use new package imports instead of deprecated.

```python
# OLD: Using langchain imports
from langchain.vectorstores import FAISS  # Deprecated!
from langchain.vectorstores import Chroma

# NEW: Use specific packages
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
```
</python>
</fix-import-packages>

<fix-embedding-consistency>
<python>

Keep embedding models consistent across operations.

```python
# BAD: Different embeddings for indexing and querying
from langchain_openai import OpenAIEmbeddings
store1 = FAISS.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))

# Later, loading with different embeddings
store2 = FAISS.load_local("./index", OpenAIEmbeddings(model="text-embedding-ada-002"))
# Queries won't work correctly!

# GOOD: Keep embedding instance consistent
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = FAISS.from_documents(docs, embeddings)
# Always use same embeddings instance
```
</python>

<typescript>

Keep embedding models consistent across operations.

```typescript
// BAD: Different embeddings for indexing and querying
const store1 = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings({ model: "text-embedding-3-small" })
);

const results = await store1.similaritySearch("query"); // Uses same embeddings

// But if you recreate:
const store2 = new MemoryVectorStore(
  new OpenAIEmbeddings({ model: "text-embedding-ada-002" }) // Different!
);
// Queries won't work correctly!

// GOOD: Keep embedding instance
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = await MemoryVectorStore.fromDocuments(docs, embeddings);
// Always use same embeddings instance
```
</typescript>
</fix-embedding-consistency>

<fix-pinecone-index-creation>
<python>

Create Pinecone index before using it.

```python
# Index doesn't auto-create
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index("nonexistent")  # Error!

# Check and create
if "my-index" not in pc.list_indexes().names():
    pc.create_index(
        name="my-index",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
```
</python>

<typescript>

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
</typescript>
</fix-pinecone-index-creation>

<fix-chroma-persistence>
<python>

Enable Chroma disk persistence.

```python
# Not persisting
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings()
)  # Ephemeral!

# Persist to disk
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)
```
</python>

<typescript>

Start Chroma server before connecting.

```typescript
// Chroma not running
import { Chroma } from "@langchain/community/vectorstores/chroma";

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
});
// Error: Connection refused!

// Start Chroma first
// Terminal: docker run -p 8000:8000 chromadb/chroma
// Or: chroma run --path ./chroma_data

const store = await Chroma.fromDocuments(docs, embeddings, {
  url: "http://localhost:8000"
}); // Works!
```
</typescript>
</fix-chroma-persistence>

<fix-dimension-mismatch>
<python>

Match embedding dimensions to index dimensions.

```python
# Pinecone index has 1536 dimensions, using 512-dim embeddings
pc.create_index(name="idx", dimension=1536, metric="cosine")

vectorstore = PineconeVectorStore.from_documents(
    docs,
    OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512),
    index=pc.Index("idx")
)  # Error: dimension mismatch!

# Match dimensions
embeddings = OpenAIEmbeddings()  # Default 1536
# Or create index with 512 dimensions
```
</python>

<typescript>

Match embedding dimensions to index dimensions.

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

// Match dimensions
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
// Default is 1536, matches Pinecone index
```
</typescript>
</fix-dimension-mismatch>

<fix-faiss-path>
<typescript>

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
</typescript>
</fix-faiss-path>

<fix-memory-ephemeral>
<python>

Memory stores are ephemeral, use FAISS instead.

```python
# Expecting persistence
vectorstore = InMemoryVectorStore(embeddings)
vectorstore.add_documents(docs)
# App restarts...
# All data is lost!

# Use persistent store for production
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("./faiss_index")  # Persists to disk
```
</python>

<typescript>

Memory stores are ephemeral, use FAISS instead.

```typescript
// Expecting persistence
const vectorStore = new MemoryVectorStore(embeddings);
await vectorStore.addDocuments(docs);
// App restarts...
// All data is lost!

// Use persistent store for production
import { FaissStore } from "@langchain/community/vectorstores/faiss";

const vectorStore = await FaissStore.fromDocuments(docs, embeddings);
await vectorStore.save("./faiss_index"); // Persists to disk
```
</typescript>
</fix-memory-ephemeral>

<fix-filter-syntax>
<typescript>

Filter syntax varies by vector store provider.

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
</typescript>
</fix-filter-syntax>

<links>
Python:
- [LangChain Python Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/)
- [FAISS](https://python.langchain.com/docs/integrations/vectorstores/faiss)
- [Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- [Pinecone](https://python.langchain.com/docs/integrations/vectorstores/pinecone)

TypeScript:
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
</links>

<installation>
Python:
```bash
# FAISS
pip install langchain-community faiss-cpu
# or faiss-gpu for GPU support

# Chroma
pip install langchain-chroma

# Pinecone
pip install langchain-pinecone pinecone-client

# Qdrant
pip install langchain-qdrant qdrant-client
```

TypeScript:
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
</installation>
