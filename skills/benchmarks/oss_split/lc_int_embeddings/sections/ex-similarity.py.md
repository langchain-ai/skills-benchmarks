Compute cosine similarity between embeddings.

```python
from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings()

# Embed query and documents
query = "What is machine learning?"
docs = [
    "Machine learning is a branch of AI",
    "Paris is the capital of France",
    "Neural networks are used in deep learning",
]

query_vec = embeddings.embed_query(query)
doc_vecs = embeddings.embed_documents(docs)

# Compute cosine similarity
def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

# Find most similar document
similarities = [cosine_similarity(query_vec, doc_vec) for doc_vec in doc_vecs]
print("Similarities:", similarities)
most_similar_idx = np.argmax(similarities)
print("Most similar doc:", docs[most_similar_idx])
```
