| Checkpointer | Use Case | Persistence | Production Ready |
|--------------|----------|-------------|------------------|
| `InMemorySaver` / `MemorySaver` | Testing, development | In-memory only | No |
| `SqliteSaver` | Local development | SQLite file | Single-user only |
| `PostgresSaver` | Production | PostgreSQL | Yes |
| `AsyncPostgresSaver` (Python) | Async production | PostgreSQL | Yes |
