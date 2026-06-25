Send creates parallel workers; reducer accumulates their results.
```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import Annotated
import operator

class State(TypedDict):
    items: list[str]
    results: Annotated[list, operator.add]  # Accumulates from parallel workers

def fan_out(state: State):
    return [Send("worker", {"item": item}) for item in state["items"]]

def worker(state: dict) -> dict:
    return {"results": [f"Processed: {state['item']}"]}

graph = (
    StateGraph(State)
    .add_node("worker", worker)
    .add_conditional_edges(START, fan_out, ["worker"])
    .add_edge("worker", END)
    .compile()
)
# invoke({"items": ["a", "b", "c"]}) -> results: ["Processed: a", "Processed: b", "Processed: c"]
```
