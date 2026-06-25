PostgreSQL for production:

```python
from langgraph.store.postgres import PostgresStore

# Use PostgreSQL for production
store = PostgresStore.from_conn_string(
    "postgresql://user:pass@localhost/db"
)

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```
