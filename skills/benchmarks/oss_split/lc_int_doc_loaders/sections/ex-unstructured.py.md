Universal loader with OCR:

```python
from langchain_community.document_loaders import UnstructuredFileLoader

# Handles PDFs, DOCXs, PPTs, images, etc.
loader = UnstructuredFileLoader("path/to/document.docx")
docs = loader.load()

# With OCR for scanned documents
loader = UnstructuredFileLoader(
    "scanned.pdf",
    strategy="ocr_only",  # Use OCR
    languages=["eng"]
)

# UnstructuredURLLoader for web pages
from langchain_community.document_loaders import UnstructuredURLLoader

loader = UnstructuredURLLoader(urls=["https://example.com"])
docs = loader.load()
```
