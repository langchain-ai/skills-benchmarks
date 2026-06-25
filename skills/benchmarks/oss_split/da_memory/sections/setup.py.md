Configure CompositeBackend with routes:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),  # Default for regular files
    routes={
        "/memories/": StoreBackend(rt),  # Persistent storage
    }
)

agent = create_deep_agent(
    backend=composite_backend,
    store=store
)

# Files with /memories/ prefix persist across threads
# Other files are ephemeral
```
