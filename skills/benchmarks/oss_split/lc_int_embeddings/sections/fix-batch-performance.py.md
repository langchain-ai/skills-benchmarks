Use batch processing instead of single calls.

```python
# Inefficient: One API call per document
embeddings = OpenAIEmbeddings()
for doc in large_doc_list:
    emb = embeddings.embed_query(doc)  # Slow!

# Efficient: Batch processing
embeddings = OpenAIEmbeddings(chunk_size=100)
all_embeddings = embeddings.embed_documents(large_doc_list)  # Fast!
```
