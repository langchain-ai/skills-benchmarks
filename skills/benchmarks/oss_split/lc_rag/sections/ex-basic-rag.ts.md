Complete RAG pipeline:

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
