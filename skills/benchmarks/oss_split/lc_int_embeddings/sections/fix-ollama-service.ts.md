Ensure Ollama service is running.

```typescript
// Ollama not running
import { OllamaEmbeddings } from "@langchain/ollama";
const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Connection error!

// Ensure Ollama is running and model is pulled
// Terminal:
// ollama pull nomic-embed-text
// ollama serve

const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Works!
```
