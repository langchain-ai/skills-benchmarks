Create vector store and perform similarity search.

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings()

texts = [
    "LangChain is a framework for developing applications powered by LLMs",
    "Vector stores enable semantic search capabilities",
    "Embeddings convert text into numerical vectors",
]

# Create vector store with embeddings
vectorstore = FAISS.from_texts(texts, embeddings)

# Perform similarity search
query = "What is LangChain?"
docs = vectorstore.similarity_search(query, k=2)
for doc in docs:
    print(doc.page_content)
```
