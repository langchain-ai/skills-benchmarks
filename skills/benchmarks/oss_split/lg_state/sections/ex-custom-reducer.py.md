Custom function to merge dictionaries:

```python
from typing import Annotated

def merge_dicts(current: dict, update: dict) -> dict:
    """Custom reducer to merge dictionaries."""
    return {**current, **update}

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]
    data: str

def update_metadata(state: State) -> dict:
    return {"metadata": {"timestamp": "2024-01-01"}}

graph = (
    StateGraph(State)
    .add_node("update", update_metadata)
    .add_edge(START, "update")
    .add_edge("update", END)
    .compile()
)

result = graph.invoke({
    "metadata": {"user": "alice"},
    "data": "test"
})
# metadata is merged: {"user": "alice", "timestamp": "2024-01-01"}
```
