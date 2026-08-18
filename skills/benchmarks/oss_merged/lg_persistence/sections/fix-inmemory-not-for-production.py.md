Use PostgresSaver instead of InMemorySaver for production persistence.
```python
# WRONG: Data lost on process restart
checkpointer = InMemorySaver()  # In-memory only!

# CORRECT: Use persistent storage for production
from langgraph.checkpoint.postgres import PostgresSaver
with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()  # only needed on first use to create tables
    graph = builder.compile(checkpointer=checkpointer)
```
