Complete RAG ingestion pipeline:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader

# Complete RAG pipeline
loader = WebBaseLoader("https://docs.example.com")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_docs = splitter.split_documents(docs)

vectorstore = FAISS.from_documents(
    split_docs,
    OpenAIEmbeddings()
)

# Ready for semantic search
results = vectorstore.similarity_search("query", k=4)
```
