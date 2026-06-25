Use new package imports instead of deprecated.

```python
# OLD: Using langchain imports
from langchain.vectorstores import FAISS  # Deprecated!
from langchain.vectorstores import Chroma

# NEW: Use specific packages
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore
```
