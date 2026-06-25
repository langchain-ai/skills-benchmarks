Explicitly allow deserialization when loading FAISS indexes.
```python
# WRONG: Will raise error
loaded_store = FAISS.load_local("./faiss_index", embeddings)

# CORRECT
loaded_store = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
```
