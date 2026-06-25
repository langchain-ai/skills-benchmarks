Chroma with persistence and metadata filtering.

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
