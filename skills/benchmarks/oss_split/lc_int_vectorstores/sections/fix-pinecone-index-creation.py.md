Create Pinecone index before using it.

```python
# Index doesn't auto-create
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index("nonexistent")  # Error!

# Check and create
if "my-index" not in pc.list_indexes().names():
    pc.create_index(
        name="my-index",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
```
