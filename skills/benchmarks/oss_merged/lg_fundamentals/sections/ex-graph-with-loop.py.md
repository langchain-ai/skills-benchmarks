Conditional edge to END prevents infinite loops.
```python
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    count: int
    max_iterations: int

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}

def should_continue(state: State) -> str:
    if state["count"] >= state["max_iterations"]:
        return END
    return "increment"

graph = (
    StateGraph(State)
    .add_node("increment", increment)
    .add_edge(START, "increment")
    .add_conditional_edges("increment", should_continue)
    .compile()
)

result = graph.invoke({"count": 0, "max_iterations": 5})
print(result["count"])  # 5
```
