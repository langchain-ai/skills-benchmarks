Match embedding dimensions to index dimensions.

```python
# Pinecone index has 1536 dimensions, using 512-dim embeddings
pc.create_index(name="idx", dimension=1536, metric="cosine")

vectorstore = PineconeVectorStore.from_documents(
    docs,
    OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512),
    index=pc.Index("idx")
)  # Error: dimension mismatch!

# Match dimensions
embeddings = OpenAIEmbeddings()  # Default 1536
# Or create index with 512 dimensions
```
