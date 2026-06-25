Use persistent storage in production:

```python
# WRONG - Data lost on restart
checkpointer = InMemorySaver()  # In-memory only!

# CORRECT - Use persistent storage
from langgraph.checkpoint.postgres import PostgresSaver
with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    graph = builder.compile(checkpointer=checkpointer)
```
