FAISS vector store with persistence.

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
