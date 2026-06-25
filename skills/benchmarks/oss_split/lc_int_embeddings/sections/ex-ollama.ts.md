Use Ollama for fully local embeddings.

```typescript
import { OllamaEmbeddings } from "@langchain/ollama";

// Requires Ollama running locally: ollama pull nomic-embed-text
const embeddings = new OllamaEmbeddings({
  model: "nomic-embed-text",
  baseUrl: "http://localhost:11434", // Default Ollama URL
});

const embedding = await embeddings.embedQuery("Fully local embeddings");
```
