File-based persistence for local development:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create SQLite checkpointer
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

graph = (
    StateGraph(State)
    .add_node("process", process_node)
    .add_edge(START, "process")
    .add_edge("process", END)
    .compile(checkpointer=checkpointer)
)

# Use with thread_id
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"data": "test"}, config)
```
