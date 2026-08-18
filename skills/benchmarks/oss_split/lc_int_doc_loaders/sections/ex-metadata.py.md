Enrich with custom metadata:

```python
from langchain_community.document_loaders import TextLoader
from datetime import datetime

loader = TextLoader("document.txt")
docs = loader.load()

# Enrich with custom metadata
for doc in docs:
    doc.metadata["loaded_at"] = datetime.now().isoformat()
    doc.metadata["category"] = "research"
```
