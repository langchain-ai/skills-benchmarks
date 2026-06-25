High-performance FAISS vector store:

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)

# Save/load
vectorstore.save_local("faiss_index")
vectorstore2 = FAISS.load_local("faiss_index", embeddings)
```
