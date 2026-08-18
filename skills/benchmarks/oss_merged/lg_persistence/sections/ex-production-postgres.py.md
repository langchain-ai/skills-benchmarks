Configure PostgreSQL-backed checkpointing for production deployments.
```python
from langgraph.checkpoint.postgres import PostgresSaver

# from_conn_string returns a context manager in v3+
with PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
) as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    graph = builder.compile(checkpointer=checkpointer)
```
