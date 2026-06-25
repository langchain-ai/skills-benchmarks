Add nodes before routing to them:

```python
# WRONG - "missing_node" not added to graph
def router(state):
    return "missing_node"

builder.add_conditional_edges("node_a", router, ["missing_node"])

# CORRECT - Add all possible destinations
builder.add_node("missing_node", func)
builder.add_conditional_edges("node_a", router, ["missing_node"])
```
