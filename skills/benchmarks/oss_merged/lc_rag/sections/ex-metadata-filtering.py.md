Add metadata to documents and filter search results by metadata properties.
```python
# Add metadata when creating documents
docs = [
    Document(
        page_content="Python programming guide",
        metadata={"language": "python", "topic": "programming"}
    ),
]

# Search with filter
results = vectorstore.similarity_search(
    "programming",
    k=5,
    filter={"language": "python"}  # Only Python docs
)
```
