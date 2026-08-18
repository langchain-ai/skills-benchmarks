Load PDF with lazy loading:

```python
from langchain_community.document_loaders import PyPDFLoader

# Load PDF file
loader = PyPDFLoader("path/to/document.pdf")
docs = loader.load()

print(f"Loaded {len(docs)} pages")
for i, doc in enumerate(docs):
    print(f"Page {i + 1}:", doc.metadata)
    print(doc.page_content[:100])

# Each page is a separate document
# metadata includes: source, page number

# Lazy loading for large PDFs
loader = PyPDFLoader("large-file.pdf")
for doc in loader.lazy_load():
    print(f"Processing page {doc.metadata['page']}")
```
