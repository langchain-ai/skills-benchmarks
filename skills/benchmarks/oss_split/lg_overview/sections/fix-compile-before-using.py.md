Compile graph before invoking:

```python
# WRONG - StateGraph is not executable
builder = StateGraph(State).add_node("node", func)
builder.invoke(...)  # Error!

# CORRECT - Must compile first
graph = builder.compile()
graph.invoke(...)
```
