Inject store via keyword parameter to access it in graph nodes.
```python
# WRONG: Store not available in node
def my_node(state):
    store.put(...)  # NameError! store not defined

# CORRECT: Inject store via keyword parameter
from langgraph.store.base import BaseStore

def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance injected
```
