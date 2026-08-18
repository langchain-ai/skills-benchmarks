Specify UTF-8 encoding:

```python
# Default encoding may fail
loader = TextLoader("file.txt")
docs = loader.load()  # UnicodeDecodeError!

# Specify encoding
loader = TextLoader("file.txt", encoding="utf-8")
docs = loader.load()
```
