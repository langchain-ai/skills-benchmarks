---
name: LangChain Vector Stores Integration (Python)
description: [LangChain] Guide to using vector store integrations in LangChain including Chroma, Pinecone, FAISS, and memory vector stores
---

<overview>
Vector stores are databases optimized for storing and searching high-dimensional vectors (embeddings). They enable semantic search by finding documents similar to a query based on vector similarity rather than keyword matching. Essential for RAG (Retrieval-Augmented Generation) systems.

### Key Concepts

- **Vector Database**: Specialized database for storing and querying embeddings
- **Similarity Search**: Finding similar documents using vector distance metrics (cosine, euclidean)
- **Metadata Filtering**: Combining vector search with metadata filters
- **Persistence**: Some vector stores run in-memory, others persist to disk/cloud
- **Scaling**: Different stores have different scalability characteristics
</overview>

<vectorstore-selection>
| Vector Store | Best For | Package | Persistence | Scalability | Key Features |
|--------------|----------|---------|-------------|-------------|--------------|
| **FAISS** | Local, high performance | `langchain-community` | Disk | Medium | Fast, CPU/GPU support, local |
| **Chroma** | Development, simplicity | `langchain-chroma` | Disk | Medium | Easy setup, local-first |
| **Pinecone** | Production, managed | `langchain-pinecone` | Cloud | High | Fully managed, auto-scaling |
| **InMemory** | Testing, prototyping | `langchain-core` | Memory only | Low | Simple, no setup, ephemeral |
| **Weaviate** | GraphQL, hybrid search | `langchain-weaviate` | Cloud/Self-hosted | High | GraphQL, hybrid search |
| **Qdrant** | High performance, filtering | `langchain-qdrant` | Cloud/Self-hosted | High | Fast, advanced filtering |
| **PGVector** | PostgreSQL users | `langchain-postgres` | PostgreSQL | High | PostgreSQL extension |
</vectorstore-selection>

<when-to-choose>
**Choose FAISS if:**
- You need high performance local vector search
- You want to avoid external dependencies
- You have many vectors (millions) to search quickly

**Choose Chroma if:**
- You want simple local development
- You need easy persistence without complex setup
- You're building a prototype or small application

**Choose Pinecone if:**
- You're building production applications
- You want zero operational overhead
- You need auto-scaling and high availability

**Choose InMemory Vector Store if:**
- You're testing or prototyping
- Data persistence isn't needed
- You want the simplest possible setup
</when-to-choose>

<ex-inmemory-vectorstore>
```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# In-memory vector store - great for testing
vectorstore = InMemoryVectorStore(OpenAIEmbeddings())

# Add documents
from langchain_core.documents import Document

docs = [
    Document(page_content="LangChain is a framework for LLM apps", metadata={"source": "docs"}),
    Document(page_content="Vector stores enable semantic search", metadata={"source": "docs"}),
    Document(page_content="Paris is the capital of France", metadata={"source": "wiki"}),
]
vectorstore.add_documents(docs)

# Similarity search
results = vectorstore.similarity_search("What is LangChain?", k=2)
for doc in results:
    print(doc.page_content)

# Search with score
results_with_score = vectorstore.similarity_search_with_score("LangChain", k=2)
for doc, score in results_with_score:
    print(f"Score: {score}, Content: {doc.page_content}")
```
</ex-inmemory-vectorstore>

<ex-faiss-vectorstore>
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import faiss

embeddings = OpenAIEmbeddings()

# Create from documents
docs = [
    Document(page_content="Document 1 content", metadata={"id": 1}),
    Document(page_content="Document 2 content", metadata={"id": 2}),
]
vectorstore = FAISS.from_documents(docs, embeddings)

# Search
results = vectorstore.similarity_search("query", k=3)

# Save to disk
vectorstore.save_local("./faiss_index")

# Load from disk
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True  # Required for loading
)

# Alternative: Initialize with specific FAISS index
embedding_dim = len(embeddings.embed_query("test"))
index = faiss.IndexFlatL2(embedding_dim)
docstore = InMemoryDocstore()
vectorstore = FAISS(embeddings, index, docstore, {})
```
</ex-faiss-vectorstore>

<ex-chroma-vectorstore>
```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Persistent Chroma (saves to disk)
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db",
    collection_name="my-collection",
)

# Search with metadata filter
results = vectorstore.similarity_search(
    "query",
    k=3,
    filter={"category": "A"}
)

# Load existing collection
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=OpenAIEmbeddings(),
    collection_name="my-collection",
)

# Delete collection
vectorstore.delete_collection()
```
</ex-chroma-vectorstore>

<ex-pinecone-vectorstore>
```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
import os

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index if it doesn't exist
index_name = "my-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embedding dimensions
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Create vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index=index,
)

# Search with metadata filter
results = vectorstore.similarity_search(
    "query",
    k=3,
    filter={"topic": "tech"}
)

# Use as retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
docs = retriever.get_relevant_documents("query")
```
</ex-pinecone-vectorstore>

<ex-incremental-add>
```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = InMemoryVectorStore(OpenAIEmbeddings())

# Add documents
vectorstore.add_documents([
    Document(page_content="Document 1", metadata={}),
])

# Add more later
vectorstore.add_documents([
    Document(page_content="Document 2", metadata={}),
    Document(page_content="Document 3", metadata={}),
])

# Or from texts
vectorstore.add_texts(
    texts=["Text 1", "Text 2"],
    metadatas=[{"source": "A"}, {"source": "B"}]
)
```
</ex-incremental-add>

<ex-as-retriever>
```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# Create vector store
vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())

# Convert to retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",  # or "mmr"
    search_kwargs={"k": 4}
)

# Use in a chain
llm = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("""
Answer based on context:
{context}

Question: {input}
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

result = retrieval_chain.invoke({"input": "What is LangChain?"})
print(result["answer"])
```
</ex-as-retriever>

<ex-mmr-search>
```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vectorstore = InMemoryVectorStore.from_texts(
    texts=["text1", "text2", "text3"],
    metadatas=[{}, {}, {}],
    embedding=OpenAIEmbeddings()
)

# MMR balances relevance and diversity
results = vectorstore.max_marginal_relevance_search(
    "query",
    k=3,
    fetch_k=10,  # Fetch 10 candidates, return 3 diverse results
    lambda_mult=0.5  # 0 = max diversity, 1 = max relevance
)
```
</ex-mmr-search>

<boundaries>
### What Agents CAN Do

* Initialize vector stores**
- Set up any supported vector store
- Configure with embeddings and connection details

* Add and query documents**
- Add documents with metadata
- Perform similarity search
- Use metadata filters

* Persist and load**
- Save vector stores to disk (FAISS, Chroma)
- Load existing vector stores
- Manage collections

* Use as retrievers**
- Convert vector stores to retrievers
- Integrate with chains and agents
- Configure search parameters

### What Agents CANNOT Do

* Mix embeddings from different models**
- Cannot use different embedding models within same vector store
- Must use consistent embeddings

* Bypass provider limits**
- Cannot exceed Pinecone index size limits
- Cannot bypass free tier restrictions

* Modify vector dimensions after creation**
- Cannot change embedding dimensions once store is created
- Must recreate store with new embeddings
</boundaries>

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

<fix-import-packages>
```python
# WRONG: OLD: Using langchain imports
from langchain.vectorstores import FAISS  # Deprecated!
from langchain.vectorstores import Chroma

# CORRECT: NEW: Use specific packages
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
```
</fix-import-packages>

<fix-pinecone-index-creation>
```python
# WRONG: Index doesn't auto-create
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index("nonexistent")  # Error!

# CORRECT: Check and create
if "my-index" not in pc.list_indexes().names():
    pc.create_index(
        name="my-index",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
```
</fix-pinecone-index-creation>

<fix-chroma-persistence>
```python
# WRONG: Not persisting
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings()
)  # Ephemeral!

# CORRECT: Persist to disk
vectorstore = Chroma.from_documents(
    docs,
    OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)
```
</fix-chroma-persistence>

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
# Or create index with 512 dimensions
```
</fix-dimension-mismatch>

<links>
### Official Documentation
- [LangChain Python Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/)
- [FAISS](https://python.langchain.com/docs/integrations/vectorstores/faiss)
- [Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- [Pinecone](https://python.langchain.com/docs/integrations/vectorstores/pinecone)

### Provider Documentation
- [FAISS Library](https://github.com/facebookresearch/faiss)
- [Chroma](https://docs.trychroma.com/)
- [Pinecone](https://docs.pinecone.io/)
- [Qdrant](https://qdrant.tech/documentation/)
</links>

<installation>
```bash
# FAISS
pip install langchain-community faiss-cpu
# or faiss-gpu for GPU support

# Chroma
pip install langchain-chroma

# Pinecone
pip install langchain-pinecone pinecone-client

# Qdrant
pip install langchain-qdrant qdrant-client
```
</installation>
