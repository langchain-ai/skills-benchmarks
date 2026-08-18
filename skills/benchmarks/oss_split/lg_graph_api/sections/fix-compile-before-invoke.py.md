Compile before invoking graph:

```python
# WRONG
builder = StateGraph(State).add_node("node", func)
builder.invoke({"input": "test"})  # AttributeError!

# CORRECT
graph = builder.compile()
graph.invoke({"input": "test"})
```
