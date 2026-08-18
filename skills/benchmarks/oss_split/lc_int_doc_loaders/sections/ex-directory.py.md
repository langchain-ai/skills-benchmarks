Bulk load from directory:

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Load all text files from directory
loader = DirectoryLoader(
    "path/to/documents",
    glob="**/*.txt",  # Pattern for files to load
    loader_cls=TextLoader
)

docs = loader.load()
print(f"Loaded {len(docs)} documents")

# With multiple file types
from langchain_community.document_loaders import PyPDFLoader

# Custom loader for different file types
def get_loader(file_path):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        return TextLoader(file_path)
```
