Add conditional exit to loops:

```python
# WRONG - Loop without exit condition
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_a")  # Infinite loop!

# CORRECT - Add conditional edge to END
def should_continue(state):
    if state["count"] > 10:
        return END
    return "node_b"

builder.add_conditional_edges("node_a", should_continue)
```
