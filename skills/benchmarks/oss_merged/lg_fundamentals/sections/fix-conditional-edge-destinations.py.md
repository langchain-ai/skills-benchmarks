Router must return names of nodes that exist in the graph.
```python
# WRONG: missing_node not added to graph
builder.add_conditional_edges("node_a", router, ["missing_node"])

# CORRECT: Add destination nodes first
builder.add_node("missing_node", func)
builder.add_conditional_edges("node_a", router, ["missing_node"])
```
