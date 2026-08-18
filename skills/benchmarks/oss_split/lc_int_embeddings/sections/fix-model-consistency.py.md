Use consistent models across all embeddings.

```python
# BAD: Using different models
embeddings1 = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings2 = OpenAIEmbeddings(model="text-embedding-ada-002")

query_vec = embeddings1.embed_query("query")
doc_vec = embeddings2.embed_query("document")
# Similarity comparison will be meaningless!

# GOOD: Use same model for everything
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
query_vec = embeddings.embed_query("query")
doc_vec = embeddings.embed_query("document")
# Now similarity makes sense
```
