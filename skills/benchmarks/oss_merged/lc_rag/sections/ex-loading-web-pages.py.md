Fetch and parse content from a web URL into a document.
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com")
docs = loader.load()
```
