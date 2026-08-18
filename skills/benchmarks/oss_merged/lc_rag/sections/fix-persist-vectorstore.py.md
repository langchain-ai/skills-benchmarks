Use persistent vector store instead of in-memory to avoid data loss.
```python
# WRONG: InMemory - lost on restart
vectorstore = InMemoryVectorStore.from_documents(docs, embeddings)

# CORRECT
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
```
