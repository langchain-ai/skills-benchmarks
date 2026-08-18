Initialize OpenAI embeddings and embed texts.

```python
from langchain_openai import OpenAIEmbeddings
import os

# Basic initialization
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),  # Optional if set in env
)

# Embed a single query
query_embedding = embeddings.embed_query(
    "What is the capital of France?"
)
print(f"Vector dimensions: {len(query_embedding)}")
print(f"First few values: {query_embedding[:5]}")

# Embed multiple documents
documents = [
    "Paris is the capital of France.",
    "London is the capital of England.",
    "Berlin is the capital of Germany.",
]
doc_embeddings = embeddings.embed_documents(documents)
print(f"Embedded {len(doc_embeddings)} documents")

# Using newer models with custom dimensions
small_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,  # Reduce from default 1536 for efficiency
)
```
