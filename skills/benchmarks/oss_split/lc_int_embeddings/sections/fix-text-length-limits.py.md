Chunk long texts before embedding.

```python
# Text too long
embeddings = OpenAIEmbeddings()
very_long_text = "..." * 100000
embeddings.embed_query(very_long_text)  # Will fail!

# Chunk long texts first
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=8000,  # OpenAI limit is ~8191 tokens
    chunk_overlap=200,
)
chunks = splitter.split_text(very_long_text)
chunk_embeddings = embeddings.embed_documents(chunks)
```
