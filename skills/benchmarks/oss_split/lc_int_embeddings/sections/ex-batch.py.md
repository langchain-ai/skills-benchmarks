Batch process large document sets efficiently.

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    chunk_size=512,  # Process in batches
)

# Efficiently embed large document sets
large_doc_set = [f"Document {i}: Some content here" for i in range(1000)]

doc_embeddings = embeddings.embed_documents(large_doc_set)
print(f"Embedded {len(doc_embeddings)} documents in batches")
```
