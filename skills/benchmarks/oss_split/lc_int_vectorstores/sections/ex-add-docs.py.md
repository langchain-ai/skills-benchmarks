Adding documents incrementally to vector store.

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
