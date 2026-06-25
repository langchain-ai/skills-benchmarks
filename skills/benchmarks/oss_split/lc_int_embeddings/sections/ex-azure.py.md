Configure Azure OpenAI embeddings.

```python
from langchain_openai import AzureOpenAIEmbeddings
import os

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="text-embedding-ada-002",
    api_version="2024-02-01",
)

embedding = embeddings.embed_query("Hello world")
print(f"Embedding length: {len(embedding)}")
```
