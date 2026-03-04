---
name: langchain-rag-pipeline-py
description: "INVOKE THIS SKILL when building ANY retrieval-augmented generation (RAG) system. Covers document loaders, RecursiveCharacterTextSplitter, embeddings (OpenAI), and vector stores (Chroma, FAISS, Pinecone). CRITICAL: Fixes for chunk size/overlap, embedding dimension mismatches, and FAISS deserialization."
---

<overview>
Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources. The pipeline:

1. **Index**: Load → Split → Embed → Store
2. **Retrieve**: Query → Embed → Search → Return docs
3. **Generate**: Docs + Query → LLM → Response

**Key Components:**
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
</overview>

<vectorstore-selection>

| Vector Store | Best For | Persistence | Key Features |
|--------------|----------|-------------|--------------|
| **InMemory** | Testing, prototyping | Memory only | Simple, no setup |
| **FAISS** | Local, high performance | Disk | Fast, CPU/GPU support |
| **Chroma** | Development, simplicity | Disk | Easy setup, local-first |
| **Pinecone** | Production, managed | Cloud | Fully managed, auto-scaling |

</vectorstore-selection>

<embedding-selection>

| Provider | Best For | Package |
|----------|----------|---------|
| **OpenAI** | General purpose, high quality | `langchain-openai` |
| **HuggingFace** | Open source, local | `langchain-huggingface` |
| **Ollama** | Fully local, privacy | `langchain-ollama` |

</embedding-selection>

---

## Complete RAG Pipeline

<ex-basic-rag-setup>
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 1. Load documents (example: in-memory text)
docs = [
    Document(page_content="LangChain is a framework for building LLM applications.", metadata={}),
    Document(page_content="RAG stands for Retrieval Augmented Generation.", metadata={}),
]

# 2. Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
splits = splitter.split_documents(docs)

# 3. Create embeddings and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore.from_documents(splits, embeddings)

# 4. Create retriever
retriever = vectorstore.as_retriever(k=4)  # Top 4 results

# 5. Use in RAG
model = ChatOpenAI(model="gpt-4.1")

query = "What is RAG?"
relevant_docs = retriever.invoke(query)

context = "\n\n".join([doc.page_content for doc in relevant_docs])
response = model.invoke([
    {"role": "system", "content": f"Use the following context to answer questions:\n\n{context}"},
    {"role": "user", "content": query},
])

print(response.content)
```
</ex-basic-rag-setup>

---

## Document Loaders

<ex-loading-pdf>
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./document.pdf")
docs = loader.load()

# Each page is a separate document with metadata including page number
print(f"Loaded {len(docs)} pages")

# Lazy loading for large PDFs
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata['page']}")
```
</ex-loading-pdf>

<ex-loading-web-pages>
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com/oss/python/langchain/agents")
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# Multiple URLs
loader = WebBaseLoader([
    "https://example.com/page1",
    "https://example.com/page2",
])
```
</ex-loading-web-pages>

<ex-loading-directory>
```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Load all text files from directory
loader = DirectoryLoader(
    "path/to/documents",
    glob="**/*.txt",  # Pattern for files to load
    loader_cls=TextLoader
)
docs = loader.load()
```
</ex-loading-directory>

---

## Text Splitting

<ex-text-splitting>
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap for context continuity
    separators=["\n\n", "\n", " ", ""],  # Split hierarchy
)

splits = splitter.split_documents(docs)
```
</ex-text-splitting>

---

## Vector Stores

<ex-faiss-vectorstore>
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)

# Save to disk
vectorstore.save_local("./faiss_index")

# Load from disk (requires allow_dangerous_deserialization)
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
```
</ex-faiss-vectorstore>

<ex-chroma-vectorstore>
```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Persistent Chroma (saves to disk)
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db",
    collection_name="my-collection",
)

# Load existing collection
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(),
    collection_name="my-collection",
)
```
</ex-chroma-vectorstore>

---

## Retrieval

<ex-similarity-search>
```python
# Basic similarity search
results = vectorstore.similarity_search(query, k=5)

# With scores
results_with_score = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results_with_score:
    print(f"Score: {score}, Content: {doc.page_content}")
```
</ex-similarity-search>

<ex-mmr-search>
```python
# MMR balances relevance and diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```
</ex-mmr-search>

<ex-metadata-filtering>
```python
# Add metadata when creating documents
docs = [
    Document(
        page_content="Python programming guide",
        metadata={"language": "python", "topic": "programming"}
    ),
]

# Search with filter
results = vectorstore.similarity_search(
    "programming",
    k=5,
    filter={"language": "python"}  # Only Python docs
)
```
</ex-metadata-filtering>

<ex-rag-with-agent>
```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_docs(query: str) -> str:
    """Search documentation for relevant information."""
    docs = retriever.invoke(query)
    return "\n\n".join([d.page_content for d in docs])

agent = create_agent(
    model="gpt-4.1",
    tools=[search_docs],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I create an agent?"}]
})
```
</ex-rag-with-agent>

<boundaries>
### What You CAN Configure

- Chunk size/overlap: Control document splitting
- Embedding model: Choose quality vs cost
- Number of results: Top-k retrieval
- Metadata filters: Filter by document properties
- Search algorithms: Similarity, MMR, hybrid

### What You CANNOT Configure

- Embedding dimensions (per model): Fixed by model
- Real-time document updates: Re-indexing needed
- Mix embeddings from different models in same store
</boundaries>

<fix-chunk-size>
```python
# WRONG: Too small - loses context
splitter = RecursiveCharacterTextSplitter(chunk_size=50)

# WRONG: Too large - hits limits
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# CORRECT: Balance (500-1500 typically good)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
```
</fix-chunk-size>

<fix-chunk-overlap>
```python
# WRONG: No overlap - context breaks at boundaries
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,  # Bad!
)

# CORRECT: Use overlap (10-20% of chunk size)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 20%
)
```
</fix-chunk-overlap>

<fix-persist-vectorstore>
```python
# WRONG: Using InMemoryVectorStore in production - lost on restart!
vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)

# CORRECT: Use persistent store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db",
)
```
</fix-persist-vectorstore>

<fix-consistent-embeddings>
```python
# WRONG: Different embeddings for index and query
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))

# Later with different model - incompatible!
retriever = vectorstore.as_retriever(embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))

# CORRECT: Use same embedding model for everything
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()  # Uses same embeddings
```
</fix-consistent-embeddings>

<fix-faiss-deserialization>
```python
# WRONG: Will raise error
loaded_store = FAISS.load_local("./faiss_index", embeddings)

# CORRECT: Must explicitly allow deserialization
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
```
</fix-faiss-deserialization>

<fix-dimension-mismatch>
```python
# WRONG: Pinecone index has 1536 dimensions, using 512-dim embeddings
pc.create_index(name="idx", dimension=1536, metric="cosine")

vectorstore = PineconeVectorStore.from_documents(
    docs,
    OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512),
    index=pc.Index("idx")
)  # Error: dimension mismatch!

# CORRECT: Match dimensions
embeddings = OpenAIEmbeddings()  # Default 1536
```
</fix-dimension-mismatch>

<fix-import-packages>
```python
# WRONG: Using deprecated imports
from langchain.vectorstores import FAISS  # Deprecated!
from langchain.document_loaders import PyPDFLoader  # Deprecated!

# CORRECT: Use specific packages
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
```
</fix-import-packages>
