Persistent vector store with Chroma:

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
