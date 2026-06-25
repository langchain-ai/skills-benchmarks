Provide store when using StoreBackend:

```python
# Missing store
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Provide store
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
