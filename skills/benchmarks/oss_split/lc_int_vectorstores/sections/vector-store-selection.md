| Vector Store | Best For | Package (Python / TypeScript) | Persistence | Scalability | Key Features |
|--------------|----------|-------------------------------|-------------|-------------|--------------|
| **FAISS** | Local, high performance | `langchain-community` / `@langchain/community` | Disk | Medium | Fast, CPU/GPU support, local |
| **Chroma** | Development, simplicity | `langchain-chroma` / `@langchain/community` | Disk | Medium | Easy setup, local-first |
| **Pinecone** | Production, managed | `langchain-pinecone` / `@langchain/pinecone` | Cloud | High | Fully managed, auto-scaling |
| **InMemory/Memory** | Testing, prototyping | `langchain-core` / `langchain/vectorstores/memory` | Memory only | Low | Simple, no setup, ephemeral |
| **Weaviate** | GraphQL, hybrid search | `langchain-weaviate` / `@langchain/weaviate` | Cloud/Self-hosted | High | GraphQL, hybrid search |
| **Qdrant** | High performance, filtering | `langchain-qdrant` / `@langchain/qdrant` | Cloud/Self-hosted | High | Fast, advanced filtering |
| **PGVector/Supabase** | PostgreSQL users | `langchain-postgres` / `@langchain/community` | PostgreSQL | High | PostgreSQL extension |
