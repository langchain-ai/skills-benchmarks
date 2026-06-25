Compile with checkpointer and breakpoints:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

graph = (
    StateGraph(State)
    .add_node("node_a", node_a)
    .add_edge(START, "node_a")
    .add_edge("node_a", END)
    .compile(
        checkpointer=checkpointer,      # Enable persistence
        interrupt_before=["node_a"],    # Breakpoint before node
        interrupt_after=["node_a"],     # Breakpoint after node
    )
)
```
