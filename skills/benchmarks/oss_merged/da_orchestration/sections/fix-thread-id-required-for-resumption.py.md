A consistent thread_id is required to resume interrupted workflows.
```python
# WRONG: Can't resume without thread_id
agent.invoke({"messages": [...]})
agent.update_state(...)  # Which thread?

# CORRECT
config = {"configurable": {"thread_id": "session-1"}}
agent.invoke({...}, config=config)
agent.update_state(config, ...)
agent.invoke(None, config=config)  # Resume
```
