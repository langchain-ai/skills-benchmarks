Fix FAISS deserialization security error.

```python
# Will raise error
loaded_store = FAISS.load_local("./faiss_index", embeddings)

# Must explicitly allow deserialization
loaded_store = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
```
