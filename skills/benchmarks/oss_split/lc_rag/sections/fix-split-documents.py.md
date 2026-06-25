Large documents exceed embedding limits. Always split first:

Split before adding to vector store:

```python
# BAD: Entire documents are too large
vectorstore.add_documents(large_docs)

# GOOD: Always split first
splits = splitter.split_documents(large_docs)
vectorstore.add_documents(splits)
```
