Ensure embedding dimensions match the vector store index dimensions.
```python
# WRONG: Index has 1536 dimensions but using 512-dim embeddings
pc.create_index(name="idx", dimension=1536, metric="cosine")
vectorstore = PineconeVectorStore.from_documents(
    docs, OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512), index=pc.Index("idx")
)  # Error: dimension mismatch!

# CORRECT: Match dimensions
embeddings = OpenAIEmbeddings()  # Default 1536
```
