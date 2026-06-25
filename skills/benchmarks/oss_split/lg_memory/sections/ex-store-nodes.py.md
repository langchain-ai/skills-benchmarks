Inject store via parameter:

```python
from langgraph.store.base import BaseStore

def my_node(state, *, store: BaseStore):
    """Store injected automatically."""
    namespace = (state["user_id"], "memories")

    # Retrieve past memories
    memories = store.search(namespace, query="preferences")

    # Save new memory
    store.put(
        namespace,
        "new_fact",
        {"fact": "User likes Python"}
    )

    return {"processed": True}

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)
```
