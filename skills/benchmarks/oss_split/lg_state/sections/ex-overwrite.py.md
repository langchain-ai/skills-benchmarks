Bypass reducer with Overwrite:

```python
from langgraph.types import Overwrite

class State(TypedDict):
    items: Annotated[list, operator.add]  # Has reducer

def reset_items(state: State) -> dict:
    # Bypass reducer and replace entire list
    return {"items": Overwrite(["new_item"])}

graph = (
    StateGraph(State)
    .add_node("reset", reset_items)
    .add_edge(START, "reset")
    .add_edge("reset", END)
    .compile()
)

result = graph.invoke({"items": ["old1", "old2"]})
print(result["items"])  # ['new_item'] (not appended)
```
