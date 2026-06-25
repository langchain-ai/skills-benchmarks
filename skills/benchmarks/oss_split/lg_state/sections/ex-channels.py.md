Low-level channel configuration:

```python
from langgraph.channels import LastValue, BinaryOperatorAggregate

class State(TypedDict):
    counter: int
    logs: list[str]

# Alternative way to define state
from langgraph.graph import StateGraph

channels = {
    "counter": BinaryOperatorAggregate(int, operator.add, default=lambda: 0),
    "logs": BinaryOperatorAggregate(list, operator.add, default=lambda: [])
}

def increment(state: dict) -> dict:
    return {"counter": 1, "logs": ["incremented"]}

graph = (
    StateGraph(State, channels=channels)
    .add_node("increment", increment)
    .add_edge(START, "increment")
    .add_edge("increment", END)
    .compile()
)
```
