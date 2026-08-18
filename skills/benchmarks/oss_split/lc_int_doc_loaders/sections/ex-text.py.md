Simple text file loading:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("path/to/file.txt")
docs = loader.load()

# Returns single document with entire file content
print(docs[0].page_content)
print(docs[0].metadata["source"])  # File path

# With specific encoding
loader = TextLoader("file.txt", encoding="utf-8")
```
