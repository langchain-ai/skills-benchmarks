Provide thread_id for persistence:

```python
# WRONG - No thread_id, state not saved
graph.invoke({"data": "test"})  # Lost after execution!

# CORRECT - Always provide thread_id
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```
