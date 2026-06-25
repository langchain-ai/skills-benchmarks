Use lazy loading:

```python
# Loading huge PDF into memory
loader = PyPDFLoader("huge-book.pdf")
docs = loader.load()  # May crash!

# Use lazy loading
for doc in loader.lazy_load():
    process_document(doc)
```
