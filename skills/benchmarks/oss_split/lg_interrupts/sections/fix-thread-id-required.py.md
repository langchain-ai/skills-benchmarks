Provide thread_id for resuming:

```python
# WRONG - No thread_id
graph.invoke({"data": "test"})  # Can't resume!

# CORRECT
config = {"configurable": {"thread_id": "session-1"}}
graph.invoke({"data": "test"}, config)
```
