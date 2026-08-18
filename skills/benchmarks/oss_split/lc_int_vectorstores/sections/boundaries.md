What You CAN Do:
- **Initialize vector stores** - Set up any supported vector store, configure with embeddings and connection details
- **Add and query documents** - Add documents with metadata, perform similarity search, use metadata filters
- **Persist and load** - Save vector stores to disk (FAISS, Chroma), load existing vector stores, manage collections
- **Use as retrievers** - Convert vector stores to retrievers, integrate with chains and agents, configure search parameters
- **Choose appropriate store** - Select based on scale, performance, persistence needs; switch between stores with minimal code changes

What You CANNOT Do:
- **Mix embeddings from different models** - Cannot use different embedding models within same vector store; must use consistent embeddings
- **Bypass provider limits** - Cannot exceed Pinecone index size limits or bypass free tier restrictions
- **Modify vector dimensions after creation** - Cannot change embedding dimensions once store is created; must recreate store with new embeddings
- **Query without proper setup** - Cannot use Chroma without server running (TypeScript), cannot use Pinecone without API key and index
