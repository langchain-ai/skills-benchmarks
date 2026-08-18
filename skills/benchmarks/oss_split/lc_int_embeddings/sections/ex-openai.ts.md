Initialize OpenAI embeddings and embed texts.

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

// Basic initialization
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  openAIApiKey: process.env.OPENAI_API_KEY, // Optional if set in env
});

// Embed a single query
const queryEmbedding = await embeddings.embedQuery(
  "What is the capital of France?"
);
console.log(`Vector dimensions: ${queryEmbedding.length}`);
console.log(`First few values: ${queryEmbedding.slice(0, 5)}`);

// Embed multiple documents
const documents = [
  "Paris is the capital of France.",
  "London is the capital of England.",
  "Berlin is the capital of Germany.",
];
const docEmbeddings = await embeddings.embedDocuments(documents);
console.log(`Embedded ${docEmbeddings.length} documents`);

// Using newer models with custom dimensions
const smallEmbeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  dimensions: 512, // Reduce from default 1536 for efficiency
});
```
