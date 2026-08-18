Use provider-specific package imports.

```python
# OLD: Using deprecated community imports
from langchain.embeddings import OpenAIEmbeddings  # Deprecated!

# NEW: Use provider-specific packages
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
```
