Parent checkpointer propagates to subgraphs:

```python
from langgraph.graph import StateGraph, START

# Only parent graph needs checkpointer
def subgraph_node(state):
    return {"data": "subgraph"}

subgraph = (
    StateGraph(State)
    .add_node("process", subgraph_node)
    .add_edge(START, "process")
    .compile()  # No checkpointer needed
)

# Parent graph with checkpointer
checkpointer = InMemorySaver()

parent = (
    StateGraph(State)
    .add_node("subgraph", subgraph)
    .add_edge(START, "subgraph")
    .compile(checkpointer=checkpointer)  # Propagates to subgraph
)
```
