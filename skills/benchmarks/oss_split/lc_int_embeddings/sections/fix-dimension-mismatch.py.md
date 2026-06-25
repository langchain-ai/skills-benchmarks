Ensure consistent embedding dimensions.

```python
# Vector store expecting 1536 dimensions, model produces 512
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
)

# Vector store initialized with different dimensions
vectorstore = FAISS.from_texts(
    ["text1"],
    OpenAIEmbeddings(),  # Uses default 1536 dimensions
)
# Adding with 512-dim embeddings will fail!

# Consistent dimensions
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_texts(["text1"], embeddings)
```
