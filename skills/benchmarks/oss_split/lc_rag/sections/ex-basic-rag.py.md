Complete RAG pipeline:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 1. Load documents (example: in-memory text)
docs = [
    Document(page_content="LangChain is a framework for building LLM applications.", metadata={}),
    Document(page_content="RAG stands for Retrieval Augmented Generation.", metadata={}),
]

# 2. Split documents
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(docs)

# 3. Create embeddings and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = InMemoryVectorStore.from_documents(splits, embeddings)

# 4. Create retriever
retriever = vectorstore.as_retriever(k=4)

# 5. Use in RAG
model = ChatOpenAI(model="gpt-4.1")
query = "What is RAG?"
relevant_docs = retriever.invoke(query)

context = "\n\n".join([doc.page_content for doc in relevant_docs])
response = model.invoke([
    {"role": "system", "content": f"Use the following context to answer questions:\n\n{context}"},
    {"role": "user", "content": query},
])
print(response.content)
```
