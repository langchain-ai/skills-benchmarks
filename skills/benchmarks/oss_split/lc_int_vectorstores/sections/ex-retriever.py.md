Vector store as retriever.

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Create vector store
vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())

# Convert to retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",  # or "mmr"
    search_kwargs={"k": 4}
)

results = retriever.invoke("What is LangChain?")
```
