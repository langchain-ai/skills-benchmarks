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
