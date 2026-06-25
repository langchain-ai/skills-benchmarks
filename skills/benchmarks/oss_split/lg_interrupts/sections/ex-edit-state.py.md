Modify state before resuming:

```python
config = {"configurable": {"thread_id": "1"}}

# Run until interrupt
graph.invoke({"data": "test"}, config)

# Modify state before resuming
graph.update_state(config, {"data": "manually edited"})

# Resume with edited state
graph.invoke(None, config)
```
