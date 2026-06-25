Use Unstructured for complex PDFs:

```python
# PyPDF may not work for complex PDFs
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("complex.pdf")
docs = loader.load()  # Poor extraction!

# Use Unstructured for complex PDFs
from langchain_community.document_loaders import UnstructuredPDFLoader
loader = UnstructuredPDFLoader("complex.pdf")
docs = loader.load()  # Better extraction
```
