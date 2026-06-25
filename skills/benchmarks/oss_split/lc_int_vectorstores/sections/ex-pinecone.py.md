Pinecone managed cloud vector store.

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
import os

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index if it doesn't exist
index_name = "my-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embedding dimensions
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Create vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index=index,
)

# Search with metadata filter
results = vectorstore.similarity_search(
    "query",
    k=3,
    filter={"topic": "tech"}
)

# Use as retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
docs = retriever.get_relevant_documents("query")
```
