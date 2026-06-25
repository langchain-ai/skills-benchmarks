Memory stores are ephemeral, use FAISS instead.

```python
# Expecting persistence
vectorstore = InMemoryVectorStore(embeddings)
vectorstore.add_documents(docs)
# App restarts...
# All data is lost!

# Use persistent store for production
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("./faiss_index")  # Persists to disk
```
