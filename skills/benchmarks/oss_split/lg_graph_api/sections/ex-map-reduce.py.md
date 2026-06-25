Fan-out with Send API:

```python
from langgraph.types import Send
from typing import Annotated
import operator

class State(TypedDict):
    items: list[str]
    results: Annotated[list, operator.add]  # Accumulate results

def fan_out(state: State):
    """Send each item to a worker node."""
    return [
        Send("worker", {"item": item})
        for item in state["items"]
    ]

def worker(state: dict) -> dict:
    """Process a single item."""
    item = state["item"]
    return {"results": [f"Processed: {item}"]}

def aggregate(state: State) -> dict:
    """Combine results."""
    return {"final": ", ".join(state["results"])}

graph = (
    StateGraph(State)
    .add_node("worker", worker)
    .add_node("aggregate", aggregate)
    .add_conditional_edges(START, fan_out, ["worker"])
    .add_edge("worker", "aggregate")
    .add_edge("aggregate", END)
    .compile()
)

result = graph.invoke({"items": ["A", "B", "C"]})
print(result["final"])  # "Processed: A, Processed: B, Processed: C"
```
