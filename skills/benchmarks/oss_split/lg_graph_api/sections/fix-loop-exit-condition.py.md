Add exit condition to loops:

```python
# WRONG - Infinite loop
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # No way out!

# CORRECT - Conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
