Use overlap (10-20% of chunk size) to maintain context at boundaries.
```python
# WRONG: No overlap - context breaks at boundaries
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# CORRECT: 10-20% overlap
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```
