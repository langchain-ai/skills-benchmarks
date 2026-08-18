Use get_stream_writer() to emit custom data.
```python
# WRONG: print() isn't streamed
def node(state):
    print("Processing...")
    return {"data": "done"}

# CORRECT
def node(state):
    writer = get_stream_writer()
    writer("Processing...")  # Streamed!
    return {"data": "done"}
```
