Append items with operator.add:

```python
from typing import Annotated
import operator

class State(TypedDict):
    items: Annotated[list, operator.add]

def add_items(state: State) -> dict:
    return {"items": ["new_item"]}

graph = (
    StateGraph(State)
    .add_node("add", add_items)
    .add_edge(START, "add")
    .add_edge("add", END)
    .compile()
)

result = graph.invoke({"items": ["old1", "old2"]})
print(result["items"])  # ['old1', 'old2', 'new_item']
```
