Chunk size 500-1500 is typically good.
```python
# WRONG: Too small (loses context) or too large (hits limits)
splitter = RecursiveCharacterTextSplitter(chunk_size=50)
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# CORRECT
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```
