Use Cohere embeddings for multilingual support.

```python
from langchain_cohere import CohereEmbeddings
import os

embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model="embed-english-v3.0",
)

query_embedding = embeddings.embed_query("Search query")
doc_embeddings = embeddings.embed_documents(["doc1", "doc2"])
```
