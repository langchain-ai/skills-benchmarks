Emit custom data from nodes:

```python
from langgraph.config import get_stream_writer

def my_node(state):
    writer = get_stream_writer()

    # Emit custom updates
    writer("Processing step 1...")
    # Do work
    writer("Processing step 2...")
    # More work
    writer("Complete!")

    return {"result": "done"}

graph = StateGraph(State).add_node("work", my_node).compile()

for chunk in graph.stream(
    {"data": "test"},
    stream_mode="custom"
):
    print(chunk)  # "Processing step 1...", etc.
```
