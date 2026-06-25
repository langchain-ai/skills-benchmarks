Retrieval Augmented Generation (RAG) enhances LLM responses by fetching relevant context from external knowledge sources. Instead of relying solely on training data, RAG systems retrieve documents at query time and use them to ground responses.

Key Concepts:
- **Document Loaders**: Ingest data from files, web, databases
- **Text Splitters**: Break documents into chunks
- **Embeddings**: Convert text to vectors
- **Vector Stores**: Store and search embeddings
- **Retrievers**: Fetch relevant documents for queries

RAG Pipeline:
1. **Index**: Load -> Split -> Embed -> Store
2. **Retrieve**: Query -> Embed -> Search -> Return docs
3. **Generate**: Docs + Query -> LLM -> Response
