Use persistent backend in production:

```python
# WRONG - Data lost on restart
store = InMemoryStore()  # Memory only!

# CORRECT - Use persistent backend
from langgraph.store.postgres import PostgresStore
store = PostgresStore.from_conn_string("postgresql://...")
```
