---
name: langchain-embeddings-integration-js
description: "[LangChain] Guide to using embedding model integrations in LangChain including OpenAI, Azure, and local embeddings"
---

<overview>
Embedding models convert text into numerical vector representations that capture semantic meaning. These vectors enable semantic search, similarity comparison, and are essential for building RAG (Retrieval-Augmented Generation) systems with vector databases.

Key Concepts:
- **Embeddings**: Dense vector representations of text that encode semantic meaning
- **Vector Dimensions**: Different models produce vectors of different sizes (e.g., 1536 for OpenAI, 768 for some open-source models)
- **Similarity Search**: Finding similar texts by comparing vector distances (cosine similarity, euclidean distance)
- **Batch Processing**: Efficiently embedding multiple texts at once
- **Use Cases**: Semantic search, document retrieval, clustering, recommendation systems
</overview>

<provider-selection>

| Provider | Best For | Model Examples | Dimensions | Package | Key Features |
|----------|----------|----------------|------------|---------|--------------|
| **OpenAI** | General purpose, high quality | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | 1536, 3072 | `@langchain/openai` | High quality, reliable, flexible dimensions |
| **Azure OpenAI** | Enterprise, compliance | text-embedding-ada-002 (Azure) | 1536 | `@langchain/openai` | Enterprise SLAs, data residency |
| **Cohere** | Multilingual, search optimization | embed-english-v3.0, embed-multilingual-v3.0 | 1024 | `@langchain/cohere` | Search/clustering modes, multilingual |
| **HuggingFace** | Open source, customizable | all-MiniLM-L6-v2, BGE models | Varies | `@langchain/community` | Free, local inference, many models |
| **Google** | GCP integration | textembedding-gecko | 768 | `@langchain/google-genai` | GCP ecosystem, multimodal |
| **Ollama** | Local, privacy | llama2, mistral, nomic-embed-text | Varies | `@langchain/ollama` | Fully local, no API costs, privacy |

</provider-selection>

<when-to-use>
**Choose OpenAI if:**
- You need high-quality embeddings for production
- You want reliable, fast API-based embeddings
- Cost is reasonable for your use case (~$0.13 per 1M tokens)

**Choose Azure OpenAI if:**
- You need enterprise support and SLAs
- Data compliance/residency is critical
- You're already using Azure infrastructure

**Choose Cohere if:**
- You need multilingual embeddings
- You want optimized embeddings for search vs. clustering
- You need competitive pricing

**Choose HuggingFace if:**
- You want to use open-source models
- You need specific model characteristics
- You want to run inference locally or on your own infrastructure

**Choose Ollama if:**
- Privacy is paramount (fully local)
- You want zero API costs after setup
- You have sufficient local compute resources
</when-to-use>

<ex-openai>
OpenAI embeddings:

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
</ex-openai>

<ex-azure>
Azure OpenAI embeddings:

```typescript
import { AzureOpenAIEmbeddings } from "@langchain/openai";

const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: process.env.AZURE_OPENAI_API_INSTANCE_NAME,
  azureOpenAIApiEmbeddingsDeploymentName: "text-embedding-ada-002",
  azureOpenAIApiVersion: "2024-02-01",
});

const embedding = await embeddings.embedQuery("Hello world");
```
</ex-azure>

<ex-huggingface>
HuggingFace local embeddings:

```typescript
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/hf_transformers";

// Run embeddings locally with Transformers.js
const embeddings = new HuggingFaceTransformersEmbeddings({
  modelName: "Xenova/all-MiniLM-L6-v2",
});

const embedding = await embeddings.embedQuery("This runs locally!");
```
</ex-huggingface>

<ex-ollama>
Ollama local embeddings:

```typescript
import { OllamaEmbeddings } from "@langchain/ollama";

// Requires Ollama running locally: ollama pull nomic-embed-text
const embeddings = new OllamaEmbeddings({
  model: "nomic-embed-text",
  baseUrl: "http://localhost:11434", // Default Ollama URL
});

const embedding = await embeddings.embedQuery("Fully local embeddings");
```
</ex-ollama>

<ex-cohere>
Cohere embeddings with input types:

```typescript
import { CohereEmbeddings } from "@langchain/cohere";

const embeddings = new CohereEmbeddings({
  apiKey: process.env.COHERE_API_KEY,
  model: "embed-english-v3.0",
  inputType: "search_query", // or "search_document", "classification", "clustering"
});

const queryEmbedding = await embeddings.embedQuery("Search query");
const docEmbeddings = await embeddings.embedDocuments(["doc1", "doc2"]);
```
</ex-cohere>

<ex-similarity>
Computing cosine similarity:

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings();

// Embed query and documents
const query = "What is machine learning?";
const docs = [
  "Machine learning is a branch of AI",
  "Paris is the capital of France",
  "Neural networks are used in deep learning",
];

const queryVec = await embeddings.embedQuery(query);
const docVecs = await embeddings.embedDocuments(docs);

// Compute cosine similarity
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
  const magnitudeA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
  const magnitudeB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
  return dotProduct / (magnitudeA * magnitudeB);
}

// Find most similar document
const similarities = docVecs.map((docVec) =>
  cosineSimilarity(queryVec, docVec)
);
console.log("Similarities:", similarities);
const mostSimilarIdx = similarities.indexOf(Math.max(...similarities));
console.log("Most similar doc:", docs[mostSimilarIdx]);
```
</ex-similarity>

<ex-batch>
Batch processing for efficiency:

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings({
  batchSize: 512, // OpenAI allows up to 2048 in one request
});

// Efficiently embed large document sets
const largeDocSet = Array.from({ length: 1000 }, (_, i) =>
  `Document ${i}: Some content here`
);

const docEmbeddings = await embeddings.embedDocuments(largeDocSet);
console.log(`Embedded ${docEmbeddings.length} documents in batches`);
```
</ex-batch>

<boundaries>
What Agents CAN Do:
- **Initialize embedding models**: Set up OpenAI, Azure, Cohere, HuggingFace, or Ollama embeddings; configure API keys and model parameters
- **Embed text content**: Embed single queries with `embedQuery()`; embed multiple documents with `embedDocuments()`; process large batches efficiently
- **Use embeddings with vector stores**: Pass embeddings to vector store constructors; enable semantic search capabilities
- **Choose appropriate models**: Select based on quality, cost, latency requirements; use local models for privacy concerns
- **Optimize for use case**: Adjust batch sizes for efficiency; use smaller dimensions to reduce costs/storage

What Agents CANNOT Do:
- **Modify embedding dimensions arbitrarily**: Cannot change dimensions beyond what the model supports; text-embedding-3-* models support custom dimensions, older models don't
- **Mix embeddings from different models**: Cannot compare embeddings from different models directly; must use same model for all embeddings in a similarity search
- **Exceed API rate limits**: Cannot bypass provider rate limits; must implement rate limiting for large-scale operations
- **Generate embeddings without proper authentication**: Cannot use cloud providers without valid API keys; cannot access models without proper credentials
</boundaries>

<fix-model-consistency>
Use same model for all embeddings:

```typescript
// BAD: Using different models
const embeddings1 = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const embeddings2 = new OpenAIEmbeddings({
  modelName: "text-embedding-ada-002"
});

const queryVec = await embeddings1.embedQuery("query");
const docVec = await embeddings2.embedQuery("document");
// Similarity comparison will be meaningless!

// GOOD: Use same model for everything
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const queryVec = await embeddings.embedQuery("query");
const docVec = await embeddings.embedQuery("document");
// Now similarity makes sense
```
</fix-model-consistency>

<fix-batch-size>
Configure appropriate batch size:

```typescript
// Potential API error with too many docs
const embeddings = new OpenAIEmbeddings();
const hugeDocs = Array(5000).fill("text");
await embeddings.embedDocuments(hugeDocs); // May fail!

// Fix: Configure appropriate batch size
const embeddings = new OpenAIEmbeddings({
  batchSize: 512, // OpenAI limit is 2048, use smaller for safety
});
await embeddings.embedDocuments(hugeDocs); // Handles batching automatically
```
</fix-batch-size>

<fix-api-keys>
Use environment variables for API keys:

```typescript
// WRONG: Hardcoded API key
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: "sk-...", // Never commit this!
});

// CORRECT: Use environment variables
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// Even better: auto-detection
const embeddings = new OpenAIEmbeddings();
// Reads OPENAI_API_KEY from environment automatically
```
</fix-api-keys>

<fix-text-length>
Chunk long texts before embedding:

```typescript
// Problem: Text too long
const embeddings = new OpenAIEmbeddings();
const veryLongText = "...".repeat(100000);
await embeddings.embedQuery(veryLongText); // Will fail!

// Fix: Chunk long texts first
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 8000, // OpenAI limit is ~8191 tokens
});
const chunks = await splitter.splitText(veryLongText);
const embeddings = await embeddings.embedDocuments(chunks);
```
</fix-text-length>

<fix-ollama-setup>
Ensure Ollama is running:

```typescript
// Ollama not running - will fail
import { OllamaEmbeddings } from "@langchain/ollama";
const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Connection error!

// Fix: Ensure Ollama is running and model is pulled
// Terminal:
// ollama pull nomic-embed-text
// ollama serve

const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Works!
```
</fix-ollama-setup>

<fix-azure-config>
Azure requires all configuration fields:

```typescript
// Problem: Missing required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// Fix: All required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiEmbeddingsDeploymentName: "text-embedding-ada-002",
  azureOpenAIApiVersion: "2024-02-01",
});
```
</fix-azure-config>

<fix-dimension-mismatch>
Match embedding dimensions to vector store:

```typescript
// Problem: Vector store expecting 1536 dimensions, model produces 512
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  dimensions: 512,
});

// Vector store created with default 1536 dimensions
const vectorStore = await MemoryVectorStore.fromTexts(
  ["text1"],
  embeddings, // Mismatch!
);

// Fix: Consistent dimensions
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  // Don't override dimensions, or ensure vector store matches
});
```
</fix-dimension-mismatch>

<documentation-links>
Official Documentation:
- [LangChain JS Embeddings Overview](https://js.langchain.com/docs/integrations/text_embedding/)
- [OpenAI Embeddings](https://js.langchain.com/docs/integrations/text_embedding/openai)
- [Azure OpenAI Embeddings](https://js.langchain.com/docs/integrations/text_embedding/azure_openai)
- [HuggingFace Embeddings](https://js.langchain.com/docs/integrations/text_embedding/hugging_face)
- [Ollama Embeddings](https://js.langchain.com/docs/integrations/text_embedding/ollama)

Provider Documentation:
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cohere Embeddings](https://docs.cohere.com/docs/embeddings)
- [HuggingFace Models](https://huggingface.co/models?pipeline_tag=feature-extraction)
- [Ollama](https://ollama.ai/)

Package Installation:
```bash
# OpenAI
npm install @langchain/openai

# Cohere
npm install @langchain/cohere

# Ollama
npm install @langchain/ollama

# Community (HuggingFace, etc.)
npm install @langchain/community
```
</documentation-links>
