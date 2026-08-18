In-memory vector store with similarity search.

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
