Provide store when using StoreBackend:

```python
# StoreBackend needs a Store
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Pass a Store instance
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
