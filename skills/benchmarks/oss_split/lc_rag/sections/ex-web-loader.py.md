Load documents from a URL:

```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://docs.langchain.com/oss/python/langchain/agents")
docs = loader.load()
print(f"Loaded {len(docs)} documents")
```
