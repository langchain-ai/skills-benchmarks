Keep embedding models consistent across operations.

```python
# BAD: Different embeddings for indexing and querying
from langchain_openai import OpenAIEmbeddings
store1 = FAISS.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))

# Later, loading with different embeddings
store2 = FAISS.load_local("./index", OpenAIEmbeddings(model="text-embedding-ada-002"))
# Queries won't work correctly!

# GOOD: Keep embedding instance consistent
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = FAISS.from_documents(docs, embeddings)
# Always use same embeddings instance
```
