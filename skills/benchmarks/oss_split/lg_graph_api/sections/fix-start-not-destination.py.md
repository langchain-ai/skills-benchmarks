Use named entry node instead:

```python
# WRONG - Cannot route back to START
builder.add_edge("node_a", START)  # Error!

# CORRECT - Use named entry node instead
builder.add_node("entry", entry_func)
builder.add_edge(START, "entry")
builder.add_edge("node_a", "entry")  # OK
```
