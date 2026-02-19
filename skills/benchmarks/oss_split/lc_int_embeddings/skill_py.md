---
name: LangChain Embeddings Integration (Python)
description: "[LangChain] Guide to using embedding model integrations in LangChain including OpenAI, Azure, and local embeddings"
---

<overview>
Embedding models convert text into numerical vector representations that capture semantic meaning. These vectors enable semantic search, similarity comparison, and are essential for building RAG (Retrieval-Augmented Generation) systems with vector databases.

### Key Concepts

- **Embeddings**: Dense vector representations of text that encode semantic meaning
- **Vector Dimensions**: Different models produce vectors of different sizes (e.g., 1536 for OpenAI, 768 for some open-source models)
- **Similarity Search**: Finding similar texts by comparing vector distances (cosine similarity, euclidean distance)
- **Batch Processing**: Efficiently embedding multiple texts at once
- **Use Cases**: Semantic search, document retrieval, clustering, recommendation systems
</overview>

<provider-selection>

| Provider | Best For | Model Examples | Dimensions | Package | Key Features |
|----------|----------|----------------|------------|---------|--------------|
| **OpenAI** | General purpose, high quality | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | 1536, 3072 | `langchain-openai` | High quality, reliable, flexible dimensions |
| **Azure OpenAI** | Enterprise, compliance | text-embedding-ada-002 (Azure) | 1536 | `langchain-openai` | Enterprise SLAs, data residency |
| **Cohere** | Multilingual, search optimization | embed-english-v3.0, embed-multilingual-v3.0 | 1024 | `langchain-cohere` | Search/clustering modes, multilingual |
| **HuggingFace** | Open source, customizable | all-MiniLM-L6-v2, BGE models | Varies | `langchain-huggingface` | Free, local inference, many models |
| **Google** | GCP integration | textembedding-gecko | 768 | `langchain-google-genai` | GCP ecosystem, multimodal |
| **Ollama** | Local, privacy | llama2, mistral, nomic-embed-text | Varies | `langchain-ollama` | Fully local, no API costs, privacy |

</provider-selection>

<when-to-choose>
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
</when-to-choose>

<ex-openai-embeddings>
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
</ex-openai-embeddings>

<ex-azure-openai-embeddings>
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
</ex-azure-openai-embeddings>

<ex-huggingface-embeddings>
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
</ex-huggingface-embeddings>

<ex-ollama-embeddings>
```python
from langchain_ollama import OllamaEmbeddings

# Requires Ollama running locally: ollama pull nomic-embed-text
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",  # Default Ollama URL
)

embedding = embeddings.embed_query("Fully local embeddings")
```
</ex-ollama-embeddings>

<ex-cohere-embeddings>
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
</ex-cohere-embeddings>

<ex-computing-similarity>
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
</ex-computing-similarity>

<ex-batch-processing>
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
</ex-batch-processing>

<ex-with-vectorstores>
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
</ex-with-vectorstores>

<boundaries>
### What Agents CAN Do

* Initialize embedding models**
- Set up OpenAI, Azure, Cohere, HuggingFace, or Ollama embeddings
- Configure API keys and model parameters

* Embed text content**
- Embed single queries with `embed_query()`
- Embed multiple documents with `embed_documents()`
- Process large batches efficiently

* Use embeddings with vector stores**
- Pass embeddings to vector store constructors
- Enable semantic search capabilities

* Choose appropriate models**
- Select based on quality, cost, latency requirements
- Use local models for privacy concerns

* Optimize for use case**
- Adjust batch sizes for efficiency
- Use smaller dimensions to reduce costs/storage

### What Agents CANNOT Do

* Modify embedding dimensions arbitrarily**
- Cannot change dimensions beyond what the model supports
- text-embedding-3-* models support custom dimensions, older models don't

* Mix embeddings from different models**
- Cannot compare embeddings from different models directly
- Must use same model for all embeddings in a similarity search

* Exceed API rate limits**
- Cannot bypass provider rate limits
- Must implement rate limiting for large-scale operations

* Generate embeddings without proper authentication**
- Cannot use cloud providers without valid API keys
- Cannot access models without proper credentials
</boundaries>

<fix-model-consistency>
```python
# WRONG: BAD: Using different models
embeddings1 = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings2 = OpenAIEmbeddings(model="text-embedding-ada-002")

query_vec = embeddings1.embed_query("query")
doc_vec = embeddings2.embed_query("document")
# Similarity comparison will be meaningless!

# CORRECT: GOOD: Use same model for everything
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
query_vec = embeddings.embed_query("query")
doc_vec = embeddings.embed_query("document")
# Now similarity makes sense
```
</fix-model-consistency>

<fix-import-packages>
```python
# WRONG: OLD: Using deprecated community imports
from langchain.embeddings import OpenAIEmbeddings  # Deprecated!

# CORRECT: NEW: Use provider-specific packages
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
```
</fix-import-packages>

<fix-text-length-limits>
```python
# WRONG: Text too long
embeddings = OpenAIEmbeddings()
very_long_text = "..." * 100000
embeddings.embed_query(very_long_text)  # Will fail!

# CORRECT: Chunk long texts first
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=8000,  # OpenAI limit is ~8191 tokens
    chunk_overlap=200,
)
chunks = splitter.split_text(very_long_text)
chunk_embeddings = embeddings.embed_documents(chunks)
```
</fix-text-length-limits>

<fix-huggingface-download>
```python
# WRONG: First run may be slow (downloading model)
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
# Downloads ~420MB on first run!

# CORRECT: Be aware and cache models
# Models are cached in ~/.cache/huggingface/
# Subsequent runs will be fast
```
</fix-huggingface-download>

<fix-azure-configuration>
```python
# WRONG: INCOMPLETE: Missing required fields
embeddings = AzureOpenAIEmbeddings(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# CORRECT: COMPLETE: All required fields
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint="https://my-instance.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="text-embedding-ada-002",
    api_version="2024-02-01",
)
```
</fix-azure-configuration>

<fix-ollama-service>
```python
# WRONG: Ollama not running
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Connection error!

# CORRECT: Ensure Ollama is running and model is pulled
# Terminal:
# ollama pull nomic-embed-text
# ollama serve

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Works!
```
</fix-ollama-service>

<fix-batch-efficiency>
```python
# WRONG: Inefficient: One API call per document
embeddings = OpenAIEmbeddings()
for doc in large_doc_list:
    emb = embeddings.embed_query(doc)  # Slow!

# CORRECT: Efficient: Batch processing
embeddings = OpenAIEmbeddings(chunk_size=100)
all_embeddings = embeddings.embed_documents(large_doc_list)  # Fast!
```
</fix-batch-efficiency>

<fix-dimension-mismatch>
```python
# WRONG: Vector store expecting 1536 dimensions, model produces 512
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

# CORRECT: Consistent dimensions
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_texts(["text1"], embeddings)
```
</fix-dimension-mismatch>

<links>
### Official Documentation
- [LangChain Python Embeddings Overview](https://python.langchain.com/docs/integrations/text_embedding/)
- [OpenAI Embeddings](https://python.langchain.com/docs/integrations/text_embedding/openai)
- [Azure OpenAI Embeddings](https://python.langchain.com/docs/integrations/text_embedding/azureopenai)
- [HuggingFace Embeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub)
- [Ollama Embeddings](https://python.langchain.com/docs/integrations/text_embedding/ollama)

### Provider Documentation
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cohere Embeddings](https://docs.cohere.com/docs/embeddings)
- [HuggingFace Models](https://huggingface.co/models?pipeline_tag=feature-extraction)
- [Ollama](https://ollama.ai/)
</links>

<installation>
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
</installation>
