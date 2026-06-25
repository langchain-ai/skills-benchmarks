Run local HuggingFace embeddings.

```python
from langchain_huggingface import HuggingFaceEmbeddings

# Run embeddings locally with sentence-transformers
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",  # Default model
    model_kwargs={"device": "cpu"},  # or "cuda" for GPU
    encode_kwargs={"normalize_embeddings": True},
)

embedding = embeddings.embed_query("This runs locally!")
print(f"Embedding dimensions: {len(embedding)}")

# Use a different model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)
```
