Load from S3 bucket:

```python
from langchain_community.document_loaders import S3FileLoader

loader = S3FileLoader(
    bucket="my-bucket",
    key="documents/file.pdf"
)
docs = loader.load()

# S3 Directory Loader
from langchain_community.document_loaders import S3DirectoryLoader

loader = S3DirectoryLoader(
    bucket="my-bucket",
    prefix="documents/"
)
docs = loader.load()
```
