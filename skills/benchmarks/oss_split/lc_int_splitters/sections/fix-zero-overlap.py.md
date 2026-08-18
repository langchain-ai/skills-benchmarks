BAD vs GOOD overlap config:

```python
# No overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,  # Context lost at boundaries
)

# Use overlap
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,  # 20% overlap
)
```
