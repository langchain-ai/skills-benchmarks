Too small loses context, too large hits limits. Use 500-1500 characters:

Optimal chunk size configuration:

```python
# BAD: Too small - loses context
splitter = RecursiveCharacterTextSplitter(chunk_size=50)

# BAD: Too large - hits limits
splitter = RecursiveCharacterTextSplitter(chunk_size=10000)

# GOOD: Balance (500-1500 typically)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```
