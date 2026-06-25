Modify state before resuming:

```python
# Modify state before resuming
config = {"configurable": {"thread_id": "1"}}

# Update state
graph.update_state(
    config,
    {"data": "manually_updated"}
)

# Resume with updated state
result = graph.invoke(None, config)
```
