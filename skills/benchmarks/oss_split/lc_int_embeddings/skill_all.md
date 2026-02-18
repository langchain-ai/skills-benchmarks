---
name: LangChain Embeddings Integration
description: "[LangChain] Guide to using embedding model integrations in LangChain including OpenAI, Azure, and local embeddings"
---

## Overview

Embedding models convert text into numerical vector representations that capture semantic meaning. These vectors enable semantic search, similarity comparison, and are essential for building RAG (Retrieval-Augmented Generation) systems with vector databases.

### Key Concepts

- **Embeddings**: Dense vector representations of text that encode semantic meaning
- **Vector Dimensions**: Different models produce vectors of different sizes (e.g., 1536 for OpenAI, 768 for some open-source models)
- **Similarity Search**: Finding similar texts by comparing vector distances (cosine similarity, euclidean distance)
- **Batch Processing**: Efficiently embedding multiple texts at once
- **Use Cases**: Semantic search, document retrieval, clustering, recommendation systems

## Provider Selection Decision Table

| Provider | Best For | Model Examples | Dimensions | Package (Python / TypeScript) | Key Features |
|----------|----------|----------------|------------|-------------------------------|--------------|
| **OpenAI** | General purpose, high quality | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | 1536, 3072 | `langchain-openai` / `@langchain/openai` | High quality, reliable, flexible dimensions |
| **Azure OpenAI** | Enterprise, compliance | text-embedding-ada-002 (Azure) | 1536 | `langchain-openai` / `@langchain/openai` | Enterprise SLAs, data residency |
| **Cohere** | Multilingual, search optimization | embed-english-v3.0, embed-multilingual-v3.0 | 1024 | `langchain-cohere` / `@langchain/cohere` | Search/clustering modes, multilingual |
| **HuggingFace** | Open source, customizable | all-MiniLM-L6-v2, BGE models | Varies | `langchain-huggingface` / `@langchain/community` | Free, local inference, many models |
| **Google** | GCP integration | textembedding-gecko | 768 | `langchain-google-genai` / `@langchain/google-genai` | GCP ecosystem, multimodal |
| **Ollama** | Local, privacy | llama2, mistral, nomic-embed-text | Varies | `langchain-ollama` / `@langchain/ollama` | Fully local, no API costs, privacy |

### When to Choose Each Provider

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

## Code Examples

### OpenAI Embeddings

#### Python

```python
from langchain_openai import OpenAIEmbeddings
import os

# Basic initialization
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),  # Optional if set in env
)

# Embed a single query
query_embedding = embeddings.embed_query(
    "What is the capital of France?"
)
print(f"Vector dimensions: {len(query_embedding)}")
print(f"First few values: {query_embedding[:5]}")

# Embed multiple documents
documents = [
    "Paris is the capital of France.",
    "London is the capital of England.",
    "Berlin is the capital of Germany.",
]
doc_embeddings = embeddings.embed_documents(documents)
print(f"Embedded {len(doc_embeddings)} documents")

# Using newer models with custom dimensions
small_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,  # Reduce from default 1536 for efficiency
)
```

#### TypeScript

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

### Azure OpenAI Embeddings

#### Python

```python
from langchain_openai import AzureOpenAIEmbeddings
import os

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="text-embedding-ada-002",
    api_version="2024-02-01",
)

embedding = embeddings.embed_query("Hello world")
print(f"Embedding length: {len(embedding)}")
```

#### TypeScript

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

### HuggingFace Embeddings (Local)

#### Python

```python
from langchain_huggingface import HuggingFaceEmbeddings

# Run embeddings locally with sentence-transformers
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",  # Default model
    model_kwargs={"device": "cpu"},  # or "cuda" for GPU
    encode_kwargs={"normalize_embeddings": True},
)

embedding = embeddings.embed_query("This runs locally!")
print(f"Embedding dimensions: {len(embedding)}")

# Use a different model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)
```

#### TypeScript

```typescript
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/hf_transformers";

// Run embeddings locally with Transformers.js
const embeddings = new HuggingFaceTransformersEmbeddings({
  modelName: "Xenova/all-MiniLM-L6-v2",
});

const embedding = await embeddings.embedQuery("This runs locally!");
```

### Ollama Embeddings (Local)

#### Python

```python
from langchain_ollama import OllamaEmbeddings

# Requires Ollama running locally: ollama pull nomic-embed-text
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",  # Default Ollama URL
)

embedding = embeddings.embed_query("Fully local embeddings")
```

#### TypeScript

```typescript
import { OllamaEmbeddings } from "@langchain/ollama";

// Requires Ollama running locally: ollama pull nomic-embed-text
const embeddings = new OllamaEmbeddings({
  model: "nomic-embed-text",
  baseUrl: "http://localhost:11434", // Default Ollama URL
});

const embedding = await embeddings.embedQuery("Fully local embeddings");
```

### Cohere Embeddings

#### Python

```python
from langchain_cohere import CohereEmbeddings
import os

embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model="embed-english-v3.0",
)

query_embedding = embeddings.embed_query("Search query")
doc_embeddings = embeddings.embed_documents(["doc1", "doc2"])
```

#### TypeScript

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

### Computing Similarity

#### Python

```python
from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings()

# Embed query and documents
query = "What is machine learning?"
docs = [
    "Machine learning is a branch of AI",
    "Paris is the capital of France",
    "Neural networks are used in deep learning",
]

query_vec = embeddings.embed_query(query)
doc_vecs = embeddings.embed_documents(docs)

# Compute cosine similarity
def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

# Find most similar document
similarities = [cosine_similarity(query_vec, doc_vec) for doc_vec in doc_vecs]
print("Similarities:", similarities)
most_similar_idx = np.argmax(similarities)
print("Most similar doc:", docs[most_similar_idx])
```

#### TypeScript

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

### Batch Processing for Efficiency

#### Python

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    chunk_size=512,  # Process in batches
)

# Efficiently embed large document sets
large_doc_set = [f"Document {i}: Some content here" for i in range(1000)]

doc_embeddings = embeddings.embed_documents(large_doc_set)
print(f"Embedded {len(doc_embeddings)} documents in batches")
```

#### TypeScript

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

### Using with Vector Stores (Python)

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings()

texts = [
    "LangChain is a framework for developing applications powered by LLMs",
    "Vector stores enable semantic search capabilities",
    "Embeddings convert text into numerical vectors",
]

# Create vector store with embeddings
vectorstore = FAISS.from_texts(texts, embeddings)

# Perform similarity search
query = "What is LangChain?"
docs = vectorstore.similarity_search(query, k=2)
for doc in docs:
    print(doc.page_content)
```

## Boundaries

### What Agents CAN Do

- **Initialize embedding models** - Set up OpenAI, Azure, Cohere, HuggingFace, or Ollama embeddings and configure API keys and model parameters
- **Embed text content** - Embed single queries with `embed_query()`/`embedQuery()`, embed multiple documents with `embed_documents()`/`embedDocuments()`, and process large batches efficiently
- **Use embeddings with vector stores** - Pass embeddings to vector store constructors and enable semantic search capabilities
- **Choose appropriate models** - Select based on quality, cost, latency requirements and use local models for privacy concerns
- **Optimize for use case** - Adjust batch sizes for efficiency and use smaller dimensions to reduce costs/storage

### What Agents CANNOT Do

- **Modify embedding dimensions arbitrarily** - Cannot change dimensions beyond what the model supports; text-embedding-3-* models support custom dimensions, older models don't
- **Mix embeddings from different models** - Cannot compare embeddings from different models directly; must use same model for all embeddings in a similarity search
- **Exceed API rate limits** - Cannot bypass provider rate limits; must implement rate limiting for large-scale operations
- **Generate embeddings without proper authentication** - Cannot use cloud providers without valid API keys; cannot access models without proper credentials

## Gotchas

### 1. Model Consistency is Critical

#### Python

```python
# ❌ BAD: Using different models
embeddings1 = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings2 = OpenAIEmbeddings(model="text-embedding-ada-002")

query_vec = embeddings1.embed_query("query")
doc_vec = embeddings2.embed_query("document")
# Similarity comparison will be meaningless!

# ✅ GOOD: Use same model for everything
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
query_vec = embeddings.embed_query("query")
doc_vec = embeddings.embed_query("document")
# Now similarity makes sense
```

#### TypeScript

```typescript
// ❌ BAD: Using different models
const embeddings1 = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const embeddings2 = new OpenAIEmbeddings({
  modelName: "text-embedding-ada-002"
});

const queryVec = await embeddings1.embedQuery("query");
const docVec = await embeddings2.embedQuery("document");
// Similarity comparison will be meaningless!

// ✅ GOOD: Use same model for everything
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small"
});
const queryVec = await embeddings.embedQuery("query");
const docVec = await embeddings.embedQuery("document");
// Now similarity makes sense
```

**Fix**: Always use the same embedding model for all texts you want to compare.

### 2. Import from Correct Packages (Python)

```python
# ❌ OLD: Using deprecated community imports
from langchain.embeddings import OpenAIEmbeddings  # Deprecated!

# ✅ NEW: Use provider-specific packages
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
```

**Fix**: Use provider-specific packages, not `langchain-community`.

### 3. Batch Size Limits (TypeScript)

```typescript
// ❌ Potential API error with too many docs
const embeddings = new OpenAIEmbeddings();
const hugeDocs = Array(5000).fill("text");
await embeddings.embedDocuments(hugeDocs); // May fail!

// ✅ Configure appropriate batch size
const embeddings = new OpenAIEmbeddings({
  batchSize: 512, // OpenAI limit is 2048, use smaller for safety
});
await embeddings.embedDocuments(hugeDocs); // Handles batching automatically
```

**Fix**: Set appropriate `batchSize` parameter for the provider.

### 4. Text Length Limits

#### Python

```python
# ❌ Text too long
embeddings = OpenAIEmbeddings()
very_long_text = "..." * 100000
embeddings.embed_query(very_long_text)  # Will fail!

# ✅ Chunk long texts first
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=8000,  # OpenAI limit is ~8191 tokens
    chunk_overlap=200,
)
chunks = splitter.split_text(very_long_text)
chunk_embeddings = embeddings.embed_documents(chunks)
```

#### TypeScript

```typescript
// ❌ Text too long
const embeddings = new OpenAIEmbeddings();
const veryLongText = "...".repeat(100000);
await embeddings.embedQuery(veryLongText); // Will fail!

// ✅ Chunk long texts first
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 8000, // OpenAI limit is ~8191 tokens
});
const chunks = await splitter.splitText(veryLongText);
const embeddings = await embeddings.embedDocuments(chunks);
```

**Fix**: Split long texts into chunks before embedding. Most models have 8k token limits.

### 5. HuggingFace Model Download (Python)

```python
# ❌ First run may be slow (downloading model)
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
# Downloads ~420MB on first run!

# ✅ Be aware and cache models
# Models are cached in ~/.cache/huggingface/
# Subsequent runs will be fast
```

**Fix**: First run downloads the model. Plan for network and disk space.

### 6. Azure Configuration Complexity

#### Python

```python
# ❌ INCOMPLETE: Missing required fields
embeddings = AzureOpenAIEmbeddings(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# ✅ COMPLETE: All required fields
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint="https://my-instance.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="text-embedding-ada-002",
    api_version="2024-02-01",
)
```

#### TypeScript

```typescript
// ❌ Missing required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// ✅ All required fields
const embeddings = new AzureOpenAIEmbeddings({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiEmbeddingsDeploymentName: "text-embedding-ada-002",
  azureOpenAIApiVersion: "2024-02-01",
});
```

**Fix**: Azure requires endpoint/instance name, deployment name, and API version.

### 7. Ollama Service Must Be Running

#### Python

```python
# ❌ Ollama not running
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Connection error!

# ✅ Ensure Ollama is running and model is pulled
# Terminal:
# ollama pull nomic-embed-text
# ollama serve

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Works!
```

#### TypeScript

```typescript
// ❌ Ollama not running
import { OllamaEmbeddings } from "@langchain/ollama";
const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Connection error!

// ✅ Ensure Ollama is running and model is pulled
// Terminal:
// ollama pull nomic-embed-text
// ollama serve

const embeddings = new OllamaEmbeddings({ model: "nomic-embed-text" });
await embeddings.embedQuery("test"); // Works!
```

**Fix**: Start Ollama service and pull the model first.

### 8. Batch Size for Performance (Python)

```python
# ❌ Inefficient: One API call per document
embeddings = OpenAIEmbeddings()
for doc in large_doc_list:
    emb = embeddings.embed_query(doc)  # Slow!

# ✅ Efficient: Batch processing
embeddings = OpenAIEmbeddings(chunk_size=100)
all_embeddings = embeddings.embed_documents(large_doc_list)  # Fast!
```

**Fix**: Use `embed_documents()` for batch processing instead of calling `embed_query()` in a loop.

### 9. Dimension Mismatch

#### Python

```python
# ❌ Vector store expecting 1536 dimensions, model produces 512
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
)

# Vector store initialized with different dimensions
vectorstore = FAISS.from_texts(
    ["text1"],
    OpenAIEmbeddings(),  # Uses default 1536 dimensions
)
# Adding with 512-dim embeddings will fail!

# ✅ Consistent dimensions
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_texts(["text1"], embeddings)
```

#### TypeScript

```typescript
// ❌ Vector store expecting 1536 dimensions, model produces 512
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  dimensions: 512,
});

// Vector store created with default 1536 dimensions
const vectorStore = await MemoryVectorStore.fromTexts(
  ["text1"],
  embeddings, // Mismatch!
);

// ✅ Consistent dimensions
const embeddings = new OpenAIEmbeddings({
  modelName: "text-embedding-3-small",
  // Don't override dimensions, or ensure vector store matches
});
```

**Fix**: Ensure all embeddings use consistent dimensions throughout your application.

### 10. API Keys in Environment (TypeScript)

```typescript
// ❌ Hardcoded API key
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: "sk-...", // Never commit this!
});

// ✅ Use environment variables
const embeddings = new OpenAIEmbeddings({
  openAIApiKey: process.env.OPENAI_API_KEY,
});

// ✅ Even better: auto-detection
const embeddings = new OpenAIEmbeddings();
// Reads OPENAI_API_KEY from environment automatically
```

**Fix**: Use environment variables for API keys.

## Links to Documentation

### Python
- [LangChain Python Embeddings Overview](https://python.langchain.com/docs/integrations/text_embedding/)
- [OpenAI Embeddings](https://python.langchain.com/docs/integrations/text_embedding/openai)
- [Azure OpenAI Embeddings](https://python.langchain.com/docs/integrations/text_embedding/azureopenai)
- [HuggingFace Embeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub)
- [Ollama Embeddings](https://python.langchain.com/docs/integrations/text_embedding/ollama)

### TypeScript
- [LangChain JS Embeddings Overview](https://js.langchain.com/docs/integrations/text_embedding/)
- [OpenAI Embeddings](https://js.langchain.com/docs/integrations/text_embedding/openai)
- [Azure OpenAI Embeddings](https://js.langchain.com/docs/integrations/text_embedding/azure_openai)
- [HuggingFace Embeddings](https://js.langchain.com/docs/integrations/text_embedding/hugging_face)
- [Ollama Embeddings](https://js.langchain.com/docs/integrations/text_embedding/ollama)

### Provider Documentation
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cohere Embeddings](https://docs.cohere.com/docs/embeddings)
- [HuggingFace Models](https://huggingface.co/models?pipeline_tag=feature-extraction)
- [Ollama](https://ollama.ai/)

### Package Installation

**Python:**
```bash
# OpenAI
pip install langchain-openai

# Cohere
pip install langchain-cohere

# HuggingFace
pip install langchain-huggingface sentence-transformers

# Ollama
pip install langchain-ollama

# Google
pip install langchain-google-genai
```

**TypeScript:**
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
