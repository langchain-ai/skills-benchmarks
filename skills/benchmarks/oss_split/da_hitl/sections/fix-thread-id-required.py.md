Use consistent thread_id to resume:

```python
# Can't resume without thread_id
agent.invoke({"messages": [...]})
agent.update_state(...)  # Which thread?

# Use consistent thread_id
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
agent.update_state(config, ...)
```
