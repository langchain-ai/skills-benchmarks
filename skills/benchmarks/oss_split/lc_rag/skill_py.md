---
name: LangChain RAG (Python)
description: "[LangChain] Build Retrieval Augmented Generation (RAG) systems with LangChain - includes embeddings, vector stores, retrievers, document loaders, and text splitting"
---

<overview>
Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources. Instead of relying solely on training data, RAG systems retrieve documents at query time and use them to ground responses.

**Key Concepts:**
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
- **Retrievers**: Fetch relevant documents for queries
</overview>

<rag-pipeline>
1. **Index**: Load → Split → Embed → Store
2. **Retrieve**: Query → Embed → Search → Return docs
3. **Generate**: Docs + Query → LLM → Response
</rag-pipeline>

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

<ex-loading-web-pages>
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com/oss/python/langchain/agents")
docs = loader.load()
print(f"Loaded {len(docs)} documents")
```
</ex-loading-web-pages>

<ex-loading-pdf>
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("./document.pdf")
docs = loader.load()
```
</ex-loading-pdf>

<ex-advanced-text-splitting>
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200,      # Overlap for context continuity
    separators=["\n\n", "\n", " ", ""],  # Split hierarchy
)

splits = splitter.split_documents(docs)
```
</ex-advanced-text-splitting>

<ex-chroma-persistent>
```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Create and populate
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    collection_name="my-docs",
    persist_directory="./chroma_db",
)

# Later: Load existing
vectorstore2 = Chroma(
    collection_name="my-docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
```
</ex-chroma-persistent>

<ex-advanced-retrieval>
```python
# Similarity search with scores
results = vectorstore.similarity_search_with_score(query, k=5)
for doc, score in results:
    print(f"Score: {score}, Content: {doc.page_content}")

# MMR (Maximum Marginal Relevance) for diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 20, "lambda_mult": 0.5, "k": 5},
)
```
</ex-advanced-retrieval>

<ex-metadata-filtering>
```python
# Add metadata when creating documents
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Python programming guide",
        metadata={"language": "python", "topic": "programming"}
    ),
    Document(
        page_content="JavaScript tutorial",
        metadata={"language": "javascript", "topic": "programming"}
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

<ex-faiss-performance>
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Create vector store
vectorstore = FAISS.from_documents(splits, embeddings)

# Save to disk
vectorstore.save_local("faiss_index")

# Load from disk
vectorstore2 = FAISS.load_local("faiss_index", embeddings)
```
</ex-faiss-performance>

<ex-customizing-embeddings>
```python
from langchain_openai import OpenAIEmbeddings

# Different embedding models
small_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536 dim
large_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # 3072 dim

# Custom dimensions (for 3rd gen models)
custom_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024  # Reduce from 3072 to save space
)
```
</ex-customizing-embeddings>

<boundaries>
### What You CAN Configure

* Chunk size/overlap**: Control document splitting
* Embedding model**: Choose quality vs cost
* Number of results**: Top-k retrieval
* Metadata filters**: Filter by document properties
* Search algorithms**: Similarity, MMR, hybrid

### What You CANNOT Configure

* Embedding dimensions** (per model): Fixed by model
* Perfect retrieval**: Semantic search has limits
* Real-time document updates**: Re-indexing needed
</boundaries>

<fix-split-documents>
```python
# WRONG: Problem: Entire documents are too large
vectorstore.add_documents(large_docs)  # May hit token limits

# CORRECT: Solution: Always split first
splits = splitter.split_documents(large_docs)
vectorstore.add_documents(splits)
```
</fix-split-documents>

<fix-chunk-size>
```python
# WRONG: Problem: Too small - loses context
splitter = RecursiveCharacterTextSplitter(chunk_size=50)

# WRONG: Problem: Too large - hits limits
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# CORRECT: Solution: Balance (500-1500 typically good)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
```
</fix-chunk-size>

<fix-chunk-overlap>
```python
# WRONG: Problem: No overlap - context breaks at boundaries
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,  # Bad!
)

# CORRECT: Solution: Use overlap (10-20% of chunk size)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 20%
)
```
</fix-chunk-overlap>

<fix-persist-vectorstore>
```python
# WRONG: Problem: Using InMemoryVectorStore in production
vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)
# Lost on restart!

# CORRECT: Solution: Use persistent store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="prod-docs",
    persist_directory="./chroma_db",
)
```
</fix-persist-vectorstore>

<fix-consistent-embeddings>
```python
# WRONG: Problem: Different embeddings for index and query
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))

# Later with different model
retriever = vectorstore.as_retriever(embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))  # Incompatible!

# CORRECT: Solution: Use same embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()  # Uses same embeddings
```
</fix-consistent-embeddings>

<links>
- [RAG Tutorial](https://docs.langchain.com/oss/python/langchain/rag)
- [Document Loaders](https://docs.langchain.com/oss/python/integrations/document_loaders/index)
- [Text Splitters](https://docs.langchain.com/oss/python/integrations/splitters/index)
- [Vector Stores](https://docs.langchain.com/oss/python/integrations/vectorstores/index)
- [Embeddings](https://docs.langchain.com/oss/python/integrations/text_embedding/openai)
</links>
