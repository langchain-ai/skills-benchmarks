Ensure Ollama service is running.

```python
# Ollama not running
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Connection error!

# Ensure Ollama is running and model is pulled
# Terminal:
# ollama pull nomic-embed-text
# ollama serve

embeddings = OllamaEmbeddings(model="nomic-embed-text")
embeddings.embed_query("test")  # Works!
```
