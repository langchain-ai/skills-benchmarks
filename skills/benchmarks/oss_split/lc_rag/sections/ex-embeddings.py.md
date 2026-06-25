Configure embedding models:

```python
from langchain_openai import OpenAIEmbeddings

# Different embedding models
small_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536 dim
large_embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # 3072 dim

# Custom dimensions (for 3rd gen models)
custom_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024  # Reduce from 3072 to save space
)
```
