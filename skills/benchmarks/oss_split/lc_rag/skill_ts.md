---
name: langchain-rag-js
description: "[LangChain] Build Retrieval Augmented Generation (RAG) systems with LangChain - includes embeddings, vector stores, retrievers, document loaders, and text splitting"
---

<overview>
Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources. Instead of relying solely on training data, RAG systems retrieve documents at query time and use them to ground responses.

**Key Concepts:**
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
- **Retrievers**: Fetch relevant documents for queries
</overview>

<rag-pipeline>
1. **Index**: Load → Split → Embed → Store
2. **Retrieve**: Query → Embed → Search → Return docs
3. **Generate**: Docs + Query → LLM → Response
</rag-pipeline>

<vector-store-selection>

| Store | When to Use | Why |
|-------|-------------|-----|
| MemoryVectorStore | Development, testing | In-memory, fast, ephemeral |
| Chroma | Local production | Persistent, open-source |
| Pinecone | Cloud, scale | Managed, fast, scalable |
| Faiss | High performance | Fast similarity search |

</vector-store-selection>

<embedding-model-selection>

| Model | When to Use | Dimension |
|-------|-------------|-----------|
| text-embedding-3-small | Cost-effective | 1536 |
| text-embedding-3-large | Best quality | 3072 |
| text-embedding-ada-002 | Legacy | 1536 |

</embedding-model-selection>

<ex-basic-rag-setup>
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
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 50,
});
const splits = await splitter.splitDocuments(docs);

// 3. Create embeddings and store
const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

const vectorStore = await MemoryVectorStore.fromDocuments(splits, embeddings);

// 4. Create retriever
const retriever = vectorStore.asRetriever(4); // Top 4 results

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
</ex-basic-rag-setup>

<ex-loading-web-pages>
```typescript
import { CheerioWebBaseLoader } from "@langchain/community/document_loaders/web/cheerio";

const loader = new CheerioWebBaseLoader(
  "https://docs.langchain.com/oss/javascript/langchain/agents"
);

const docs = await loader.load();
console.log(`Loaded ${docs.length} documents`);
```
</ex-loading-web-pages>

<ex-loading-pdf-files>
```typescript
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";

const loader = new PDFLoader("./document.pdf");
const docs = await loader.load();
```
</ex-loading-pdf-files>

<ex-advanced-text-splitting>
```typescript
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,        // Characters per chunk
  chunkOverlap: 200,      // Overlap for context continuity
  separators: ["\n\n", "\n", " ", ""],  // Split hierarchy
});

const splits = await splitter.splitDocuments(docs);
```
</ex-advanced-text-splitting>

<ex-using-chroma-persistent>
```typescript
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Create and populate
const vectorStore = await Chroma.fromDocuments(
  splits,
  embeddings,
  { collectionName: "my-docs" }
);

// Later: Load existing
const vectorStore2 = await Chroma.fromExistingCollection(
  embeddings,
  { collectionName: "my-docs" }
);
```
</ex-using-chroma-persistent>

<ex-advanced-retrieval>
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
</ex-advanced-retrieval>

<ex-metadata-filtering>
```typescript
// Add metadata when creating documents
const docs = [
  {
    pageContent: "Python programming guide",
    metadata: { language: "python", topic: "programming" }
  },
  {
    pageContent: "JavaScript tutorial",
    metadata: { language: "javascript", topic: "programming" }
  },
];

// Search with filter
const results = await vectorStore.similaritySearch(
  "programming",
  5,
  { language: "python" }  // Only Python docs
);
```
</ex-metadata-filtering>

<ex-rag-with-agent>
```typescript
import { createAgent } from "langchain";
import { tool } from "langchain";
import { z } from "zod";

const searchDocs = tool(
  async ({ query }) => {
    const docs = await retriever.invoke(query);
    return docs.map(d => d.pageContent).join("\n\n");
  },
  {
    name: "search_docs",
    description: "Search documentation for relevant information",
    schema: z.object({
      query: z.string().describe("Search query"),
    }),
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
</ex-rag-with-agent>

<ex-hybrid-search-keywords-semantic>
```typescript
// Combine keyword and vector search
import { similarity } from "ml-distance";

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
</ex-hybrid-search-keywords-semantic>

<boundaries>
**What You CAN Configure:**
* Chunk size/overlap: Control document splitting
* Embedding model: Choose quality vs cost
* Number of results: Top-k retrieval
* Metadata filters: Filter by document properties
* Search algorithms: Similarity, MMR, hybrid

**What You CANNOT Configure:**
* Embedding dimensions (per model): Fixed by model
* Perfect retrieval: Semantic search has limits
* Real-time document updates: Re-indexing needed
</boundaries>

<fix-forgetting-to-split-documents>
```typescript
// WRONG: Entire documents are too large
await vectorStore.addDocuments(largeDocs);  // May hit token limits

// CORRECT: Always split first
const splits = await splitter.splitDocuments(largeDocs);
await vectorStore.addDocuments(splits);
```
</fix-forgetting-to-split-documents>

<fix-chunk-size-too-small-large>
```typescript
// WRONG: Too small - loses context
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 50 });

// WRONG: Too large - hits limits
const splitter = new RecursiveCharacterTextSplitter({ chunkSize: 10000 });

// CORRECT: Balance (500-1500 typically good)
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});
```
</fix-chunk-size-too-small-large>

<fix-no-overlap>
```typescript
// WRONG: No overlap - context breaks at boundaries
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 0,  // Bad!
});

// CORRECT: Use overlap (10-20% of chunk size)
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,  // 20%
});
```
</fix-no-overlap>

<fix-not-persisting-vector-store>
```typescript
// WRONG: Using MemoryVectorStore in production
const vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);
// Lost on restart!

// CORRECT: Use persistent store
const vectorStore = await Chroma.fromDocuments(
  docs,
  embeddings,
  { collectionName: "prod-docs" }
);
```
</fix-not-persisting-vector-store>

<documentation-links>
- [RAG Tutorial](https://docs.langchain.com/oss/javascript/langchain/rag)
- [Document Loaders](https://docs.langchain.com/oss/javascript/integrations/document_loaders/index)
- [Text Splitters](https://docs.langchain.com/oss/javascript/integrations/splitters/index)
- [Vector Stores](https://docs.langchain.com/oss/javascript/integrations/vectorstores/index)
- [Embeddings](https://docs.langchain.com/oss/javascript/integrations/text_embedding/openai)
</documentation-links>
