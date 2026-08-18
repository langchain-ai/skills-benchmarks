Use get_stream_writer for custom data:

```python
# WRONG - No writer, nothing streamed
def node(state):
    print("Processing...")  # Not streamed!
    return {"data": "done"}

# CORRECT
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer("Processing...")  # Streamed!
    return {"data": "done"}
```
