Use Ollama for fully local embeddings.

```python
from langchain_ollama import OllamaEmbeddings

# Requires Ollama running locally: ollama pull nomic-embed-text
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",  # Default Ollama URL
)

embedding = embeddings.embed_query("Fully local embeddings")
```
