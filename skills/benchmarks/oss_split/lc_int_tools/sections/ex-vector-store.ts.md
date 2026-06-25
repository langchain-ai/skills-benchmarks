Convert vector store retriever to agent tool.

```typescript
import { createRetrieverTool } from "langchain/tools/retriever";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

// Create vector store
const vectorStore = await MemoryVectorStore.fromTexts(
  ["LangChain is a framework...", "Agents use tools..."],
  [{}, {}],
  new OpenAIEmbeddings()
);

// Convert to tool
const retrieverTool = createRetrieverTool(
  vectorStore.asRetriever(),
  {
    name: "knowledge_base",
    description: "Search the knowledge base for information about LangChain",
  }
);

// Use in agent
const agent = createAgent({
  model: "gpt-4.1",
  tools: [retrieverTool],
});
```
