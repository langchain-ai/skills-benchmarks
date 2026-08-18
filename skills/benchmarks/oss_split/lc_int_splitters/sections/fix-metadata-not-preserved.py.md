Preserve metadata with split_documents:

```python
# split_text loses metadata
chunks = splitter.split_text(text)

# Use split_documents
docs = [Document(page_content=text, metadata={"source": "file"})]
chunks = splitter.split_documents(docs)
```
