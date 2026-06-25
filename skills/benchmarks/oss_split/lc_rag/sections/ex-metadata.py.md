Filter search by metadata:

```python
from langchain_core.documents import Document

docs = [
    Document(page_content="Python programming guide", metadata={"language": "python", "topic": "programming"}),
    Document(page_content="JavaScript tutorial", metadata={"language": "javascript", "topic": "programming"}),
]

# Search with filter
results = vectorstore.similarity_search("programming", k=5, filter={"language": "python"})
```
