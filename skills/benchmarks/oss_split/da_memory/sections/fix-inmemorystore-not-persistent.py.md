Use PostgresStore for production:

```python
# InMemoryStore lost on restart
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Lost when process ends

# Use PostgresStore for production
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string="postgresql://...")
```
