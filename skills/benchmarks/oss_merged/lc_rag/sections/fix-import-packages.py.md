Use specific packages instead of deprecated langchain imports.
```python
# WRONG: Deprecated
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader

# CORRECT
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
```
