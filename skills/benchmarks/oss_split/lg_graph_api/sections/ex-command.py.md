Command combining state and routing:

```python
from langgraph.types import Command
from typing import Literal

class State(TypedDict):
    count: int
    result: str

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    """Update state AND decide next node."""
    new_count = state["count"] + 1

    if new_count > 5:
        # Go to node_c
        return Command(
            update={"count": new_count, "result": "Going to C"},
            goto="node_c"
        )
    else:
        # Go to node_b
        return Command(
            update={"count": new_count, "result": "Going to B"},
            goto="node_b"
        )

def node_b(state: State) -> dict:
    return {"result": f"B executed, count={state['count']}"}

def node_c(state: State) -> dict:
    return {"result": f"C executed, count={state['count']}"}

graph = (
    StateGraph(State)
    .add_node("node_a", node_a)
    .add_node("node_b", node_b)
    .add_node("node_c", node_c)
    .add_edge(START, "node_a")
    .add_edge("node_b", END)
    .add_edge("node_c", END)
    .compile()
)

result = graph.invoke({"count": 0})
print(result["result"])  # "B executed, count=1"

result = graph.invoke({"count": 5})
print(result["result"])  # "C executed, count=6"
```
