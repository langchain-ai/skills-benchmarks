Stream large files:

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("large-file.pdf")

# Stream documents one at a time
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata.get('page', 0)}")
    # Process without loading all pages into memory
```
