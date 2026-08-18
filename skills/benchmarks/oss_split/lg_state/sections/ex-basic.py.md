Simple state with partial updates:

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    processed: str
    count: int

def process(state: State) -> dict:
    return {
        "processed": state["input"].upper(),
        "count": state.get("count", 0) + 1
    }

graph = (
    StateGraph(State)
    .add_node("process", process)
    .add_edge(START, "process")
    .add_edge("process", END)
    .compile()
)

result = graph.invoke({"input": "hello", "count": 0})
print(result)  # {'input': 'hello', 'processed': 'HELLO', 'count': 1}
```
