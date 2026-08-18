START is entry-only - cannot route back to it.
```python
# WRONG
builder.add_edge("node_a", START)  # Error!

# CORRECT: Use a named entry node for loops
builder.add_node("entry", entry_func)
builder.add_edge(START, "entry")
builder.add_edge("node_a", "entry")
```
