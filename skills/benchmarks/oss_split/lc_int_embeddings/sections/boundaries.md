What You CAN Do:
- **Initialize embedding models** - Set up OpenAI, Azure, Cohere, HuggingFace, or Ollama embeddings and configure API keys and model parameters
- **Embed text content** - Embed single queries with `embed_query()`/`embedQuery()`, embed multiple documents with `embed_documents()`/`embedDocuments()`, and process large batches efficiently
- **Use embeddings with vector stores** - Pass embeddings to vector store constructors and enable semantic search capabilities
- **Choose appropriate models** - Select based on quality, cost, latency requirements and use local models for privacy concerns
- **Optimize for use case** - Adjust batch sizes for efficiency and use smaller dimensions to reduce costs/storage

What You CANNOT Do:
- **Modify embedding dimensions arbitrarily** - Cannot change dimensions beyond what the model supports; text-embedding-3-* models support custom dimensions, older models don't
- **Mix embeddings from different models** - Cannot compare embeddings from different models directly; must use same model for all embeddings in a similarity search
- **Exceed API rate limits** - Cannot bypass provider rate limits; must implement rate limiting for large-scale operations
- **Generate embeddings without proper authentication** - Cannot use cloud providers without valid API keys; cannot access models without proper credentials
