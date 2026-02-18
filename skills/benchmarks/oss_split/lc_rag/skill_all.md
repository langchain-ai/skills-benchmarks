---
name: LangChain RAG
description: "[LangChain] Build Retrieval Augmented Generation (RAG) systems with LangChain - includes embeddings, vector stores, retrievers, document loaders, and text splitting"
---

## Overview

Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources. Instead of relying solely on training data, RAG systems retrieve documents at query time and use them to ground responses.

**Key Concepts:**
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
- **Retrievers**: Fetch relevant documents for queries

**RAG Pipeline:**
1. **Index**: Load → Split → Embed → Store
2. **Retrieve**: Query → Embed → Search → Return docs
3. **Generate**: Docs + Query → LLM → Response

## Decision Tables

### Vector Store Selection

| Store | When to Use | Why |
|-------|-------------|-----|
| InMemory/MemoryVectorStore | Development, testing | In-memory, fast, ephemeral |
| Chroma | Local production | Persistent, open-source |
| Pinecone | Cloud, scale | Managed, fast, scalable |
| Faiss | High performance | Fast similarity search |

### Embedding Model Selection

| Model | When to Use | Dimension |
|-------|-------------|-----------|
| text-embedding-3-small | Cost-effective | 1536 |
| text-embedding-3-large | Best quality | 3072 |
| text-embedding-ada-002 | Legacy | 1536 |

## Code Examples

### Basic RAG Setup

#### Python

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

# 1. Load documents (example: in-memory text)
docs = [
    Document(page_content="LangChain is a framework for building LLM applications.", metadata={}),
    Document(page_content="RAG stands for Retrieval Augmented Generation.", metadata={}),
]

# 2. Split documents
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(docs)

# 3. Create embeddings and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore.from_documents(splits, embeddings)

# 4. Create retriever
retriever = vectorstore.as_retriever(k=4)

# 5. Use in RAG
model = ChatOpenAI(model="gpt-4.1")
query = "What is RAG?"
relevant_docs = retriever.invoke(query)

context = "\n\n".join([doc.page_content for doc in relevant_docs])
response = model.invoke([
    {"role": "system", "content": f"Use the following context to answer questions:\n\n{context}"},
    {"role": "user", "content": query},
])
print(response.content)
```

#### TypeScript

```typescript
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// 1. Load documents (example: in-memory text)
const docs = [
  { pageContent: "LangChain is a framework for building LLM applications.", metadata: {} },
  { pageContent: "RAG stands for Retrieval Augmented Generation.", metadata: {} },
];

// 2. Split documents
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 500, chunkOverlap: 50 });
const splits = await splitter.splitDocuments(docs);

// 3. Create embeddings and store
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorStore = await MemoryVectorStore.fromDocuments(splits, embeddings);

// 4. Create retriever
const retriever = vectorStore.asRetriever(4);

// 5. Use in RAG
const model = new ChatOpenAI({ model: "gpt-4.1" });
const query = "What is RAG?";
const relevantDocs = await retriever.invoke(query);

const context = relevantDocs.map(doc => doc.pageContent).join("\n\n");
const response = await model.invoke([
  { role: "system", content: `Use the following context to answer questions:\n\n${context}` },
  { role: "user", content: query },
]);
console.log(response.content);
```

### Loading Web Pages

#### Python

```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com/oss/python/langchain/agents")
docs = loader.load()
print(f"Loaded {len(docs)} documents")
```

#### TypeScript

```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://docs.langchain.com/oss/javascript/langchain/agents");
const docs = await loader.load();
console.log(`Loaded ${docs.length} documents`);
```

### Loading PDF Files

#### Python

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./document.pdf")
docs = loader.load()
```

#### TypeScript

```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("./document.pdf");
const docs = await loader.load();
```

### Advanced Text Splitting

#### Python

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""],
)
splits = splitter.split_documents(docs)
```

#### TypeScript

```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
  separators: ["\n\n", "\n", " ", ""],
});
const splits = await splitter.splitDocuments(docs);
```

### Using Chroma (Persistent)

#### Python

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Create and populate
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    collection_name="my-docs",
    persist_directory="./chroma_db",
)

# Later: Load existing
vectorstore2 = Chroma(
    collection_name="my-docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
```

#### TypeScript

```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Create and populate
const vectorStore = await Chroma.fromDocuments(splits, embeddings, { collectionName: "my-docs" });

// Later: Load existing
const vectorStore2 = await Chroma.fromExistingCollection(embeddings, { collectionName: "my-docs" });
```

### Advanced Retrieval

#### Python

```python
# Similarity search with scores
results = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results:
    print(f"Score: {score}, Content: {doc.page_content}")

# MMR (Maximum Marginal Relevance) for diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```

#### TypeScript

```typescript
// Similarity search with scores
const results = await vectorStore.similaritySearchWithScore(query, 5);
for (const [doc, score] of results) {
  console.log(`Score: ${score}, Content: ${doc.pageContent}`);
}

// MMR (Maximum Marginal Relevance) for diversity
const retriever = vectorStore.asRetriever({
  searchType: "mmr",
  searchKwargs: { fetchK: 20, lambda: 0.5 },
  k: 5,
});
```

### Metadata Filtering

#### Python

```python
from langchain.schema import Document

docs = [
    Document(page_content="Python programming guide", metadata={"language": "python", "topic": "programming"}),
    Document(page_content="JavaScript tutorial", metadata={"language": "javascript", "topic": "programming"}),
]

# Search with filter
results = vectorstore.similarity_search("programming", k=5, filter={"language": "python"})
```

#### TypeScript

```typescript
const docs = [
  { pageContent: "Python programming guide", metadata: { language: "python", topic: "programming" } },
  { pageContent: "JavaScript tutorial", metadata: { language: "javascript", topic: "programming" } },
];

// Search with filter
const results = await vectorStore.similaritySearch("programming", 5, { language: "python" });
```

### Using FAISS for Performance

#### Python

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)

# Save/load
vectorstore.save_local("faiss_index")
vectorstore2 = FAISS.load_local("faiss_index", embeddings)
```

### RAG with Agent

#### Python

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_docs(query: str) -> str:
    """Search documentation for relevant information."""
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

agent = create_agent(
    model="gpt-4.1",
    tools=[search_docs],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I create an agent?"}]
})
```

#### TypeScript

```typescript
import { createAgent, tool } from "langchain";
import { z } from "zod";

const searchDocs = tool(
  async ({ query }) => {
    const docs = await retriever.invoke(query);
    return docs.map(d => d.pageContent).join("\n\n");
  },
  {
    name: "search_docs",
    description: "Search documentation for relevant information",
    schema: z.object({ query: z.string().describe("Search query") }),
  }
);

const agent = createAgent({
  model: "gpt-4.1",
  tools: [searchDocs],
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "How do I create an agent?" }],
});
```

### Customizing Embeddings

#### Python

```python
from langchain_openai import OpenAIEmbeddings

# Different embedding models
small_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536 dim
large_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # 3072 dim

# Custom dimensions (for 3rd gen models)
custom_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024  # Reduce from 3072 to save space
)
```

#### TypeScript

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

// Different embedding models
const smallEmbeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });  // 1536 dim
const largeEmbeddings = new OpenAIEmbeddings({ model: "text-embedding-3-large" });  // 3072 dim

// Custom dimensions (for 3rd gen models)
const customEmbeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-large",
  dimensions: 1024,  // Reduce from 3072 to save space
});
```

### Hybrid Search (Keywords + Semantic)

#### TypeScript

```typescript
// Combine keyword and vector search
async function hybridSearch(query: string, k: number = 5) {
  // Vector search
  const vectorResults = await vectorStore.similaritySearch(query, k);

  // Keyword search (simple example)
  const allDocs = await vectorStore.getAllDocuments();
  const keywordResults = allDocs.filter(doc =>
    doc.pageContent.toLowerCase().includes(query.toLowerCase())
  );

  // Combine and deduplicate
  const combined = [...vectorResults, ...keywordResults];
  const unique = Array.from(new Set(combined.map(d => d.pageContent)))
    .map(content => combined.find(d => d.pageContent === content));

  return unique.slice(0, k);
}
```

## Boundaries

### What You CAN Configure

- **Chunk size/overlap**: Control document splitting
- **Embedding model**: Choose quality vs cost
- **Number of results**: Top-k retrieval
- **Metadata filters**: Filter by document properties
- **Search algorithms**: Similarity, MMR, hybrid

### What You CANNOT Configure

- **Embedding dimensions** (per model): Fixed by model
- **Perfect retrieval**: Semantic search has limits
- **Real-time document updates**: Re-indexing needed

## Gotchas

### 1. Forgetting to Split Documents

#### Python

```python
# BAD: Entire documents are too large
vectorstore.add_documents(large_docs)

# GOOD: Always split first
splits = splitter.split_documents(large_docs)
vectorstore.add_documents(splits)
```

#### TypeScript

```typescript
// BAD: Entire documents are too large
await vectorStore.addDocuments(largeDocs);

// GOOD: Always split first
const splits = await splitter.splitDocuments(largeDocs);
await vectorStore.addDocuments(splits);
```

### 2. Chunk Size Too Small/Large

```python
# BAD: Too small - loses context
splitter = RecursiveCharacterTextSplitter(chunk_size=50)

# BAD: Too large - hits limits
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# GOOD: Balance (500-1500 typically)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

### 3. No Overlap Between Chunks

Use 10-20% overlap of chunk size to maintain context across boundaries.

### 4. Not Persisting Vector Store

Use Chroma or FAISS with persistence for production - InMemory/MemoryVectorStore is lost on restart.

### 5. Mixing Embedding Models

#### Python

```python
# BAD: Different embeddings for index and query
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))
# Later with different model - incompatible!
retriever = vectorstore.as_retriever(embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))

# GOOD: Use same embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()  # Uses same embeddings
```

## Links to Documentation

- Python: [RAG Tutorial](https://docs.langchain.com/oss/python/langchain/rag) | [Document Loaders](https://docs.langchain.com/oss/python/integrations/document_loaders/index) | [Vector Stores](https://docs.langchain.com/oss/python/integrations/vectorstores/index)
- TypeScript: [RAG Tutorial](https://docs.langchain.com/oss/javascript/langchain/rag) | [Document Loaders](https://docs.langchain.com/oss/javascript/integrations/document_loaders/index) | [Vector Stores](https://docs.langchain.com/oss/javascript/integrations/vectorstores/index)
