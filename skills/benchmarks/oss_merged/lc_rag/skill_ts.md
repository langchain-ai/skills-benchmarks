---
name: LangChain RAG Pipeline (TypeScript)
description: "INVOKE THIS SKILL when building ANY retrieval-augmented generation (RAG) system. Covers document loaders, RecursiveCharacterTextSplitter, embeddings (OpenAI), and vector stores (Chroma, FAISS, Pinecone). CRITICAL: Fixes for chunk size/overlap, embedding dimension mismatches, and FAISS deserialization."
---

<overview>
Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources.

**Pipeline:**
1. **Index**: Load -> Split -> Embed -> Store
2. **Retrieve**: Query -> Embed -> Search -> Return docs
3. **Generate**: Docs + Query -> LLM -> Response

**Key Components:**
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
</overview>

<vectorstore-selection>

| Vector Store | Use Case | Persistence |
|--------------|----------|-------------|
| **InMemory** | Testing | Memory only |
| **FAISS** | Local, high performance | Disk |
| **Chroma** | Development | Disk |
| **Pinecone** | Production, managed | Cloud |

</vectorstore-selection>

---

## Complete RAG Pipeline

<ex-basic-rag-setup>
End-to-end RAG pipeline: load documents, split into chunks, embed, store, retrieve, and generate a response.
```typescript
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { Document } from "@langchain/core/documents";

// 1. Load documents
const docs = [
  new Document({ pageContent: "LangChain is a framework for LLM apps.", metadata: {} }),
  new Document({ pageContent: "RAG = Retrieval Augmented Generation.", metadata: {} }),
];

// 2. Split documents
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 500, chunkOverlap: 50 });
const splits = await splitter.splitDocuments(docs);

// 3. Create embeddings and store
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorstore = await MemoryVectorStore.fromDocuments(splits, embeddings);

// 4. Create retriever
const retriever = vectorstore.asRetriever({ k: 4 });

// 5. Use in RAG
const model = new ChatOpenAI({ model: "gpt-4" });
const query = "What is RAG?";
const relevantDocs = await retriever.invoke(query);

const context = relevantDocs.map(doc => doc.pageContent).join("\n\n");
const response = await model.invoke([
  { role: "system", content: `Use this context:\n\n${context}` },
  { role: "user", content: query },
]);
```
</ex-basic-rag-setup>

---

## Document Loaders

<ex-loading-pdf>
Load a PDF file and extract each page as a separate document.
```typescript
import { PDFLoader } from "langchain/document_loaders/fs/pdf";

const loader = new PDFLoader("./document.pdf");
const docs = await loader.load();
console.log(`Loaded ${docs.length} pages`);
```
</ex-loading-pdf>

<ex-loading-web-pages>
Fetch and parse content from a web URL into a document using Cheerio.
```typescript
import { CheerioWebBaseLoader } from "langchain/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader("https://docs.langchain.com");
const docs = await loader.load();
```
</ex-loading-web-pages>

---

## Vector Stores

<ex-chroma-vectorstore>
Create a Chroma vector store connected to a running Chroma server.
```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorstore = await Chroma.fromDocuments(
  splits,
  new OpenAIEmbeddings(),
  { collectionName: "my-collection", url: "http://localhost:8000" }
);
```
</ex-chroma-vectorstore>

<ex-faiss-vectorstore>
Create a FAISS vector store, save it to disk, and reload it.
```typescript
import { FaissStore } from "@langchain/community/vectorstores/faiss";

const vectorstore = await FaissStore.fromDocuments(splits, embeddings);
await vectorstore.save("./faiss_index");

const loaded = await FaissStore.load("./faiss_index", embeddings);
```
</ex-faiss-vectorstore>

---

## Retrieval

<ex-similarity-search>
Perform similarity search and retrieve results with relevance scores.
```typescript
// Basic search
const results = await vectorstore.similaritySearch(query, 5);

// With scores
const resultsWithScore = await vectorstore.similaritySearchWithScore(query, 5);
for (const [doc, score] of resultsWithScore) {
  console.log(`Score: ${score}, Content: ${doc.pageContent}`);
}
```
</ex-similarity-search>

<boundaries>
### What You CAN Configure

- Chunk size/overlap
- Embedding model
- Number of results (k)
- Metadata filters
- Search algorithms: Similarity, MMR

### What You CANNOT Configure

- Embedding dimensions (per model)
- Mix embeddings from different models in same store
</boundaries>

<fix-chunk-size>
Shows wrong and correct chunk size settings for text splitting.
```typescript
// WRONG: Too small
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 50 });

// CORRECT: Balance
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });
```
</fix-chunk-size>

<fix-persist-vectorstore>
Use a persistent vector store instead of in-memory to avoid data loss on restart.
```typescript
// WRONG: Memory - lost on restart
const vectorstore = await MemoryVectorStore.fromDocuments(docs, embeddings);

// CORRECT: Use persistent store
const vectorstore = await Chroma.fromDocuments(docs, embeddings, {
  collectionName: "my-collection",
});
```
</fix-persist-vectorstore>

<fix-consistent-embeddings>
Always use the same embedding model for indexing and querying.
```typescript
// CORRECT: Use same embedding model
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const vectorstore = await Chroma.fromDocuments(docs, embeddings);
const retriever = vectorstore.asRetriever();  // Uses same embeddings
```
</fix-consistent-embeddings>
