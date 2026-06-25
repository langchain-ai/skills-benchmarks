Full state after each step:

```python
from langgraph.graph import StateGraph, START, END

def process(state):
    return {"count": state["count"] + 1}

graph = StateGraph(State).add_node("process", process).add_edge(START, "process").add_edge("process", END).compile()

# Stream full state after each step
for chunk in graph.stream(
    {"count": 0},
    stream_mode="values"
):
    print(chunk)  # {'count': 0}, then {'count': 1}
```
