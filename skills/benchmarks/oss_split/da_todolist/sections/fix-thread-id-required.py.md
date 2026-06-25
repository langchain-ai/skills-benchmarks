Use thread_id for persistence:

```python
# Todo list won't persist without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Task 1"}]})
agent.invoke({"messages": [{"role": "user", "content": "Task 2"}]})

# Use thread_id for persistence
config = {"configurable": {"thread_id": "user-session"}}
agent.invoke({"messages": [{"role": "user", "content": "Task 1"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "Task 2"}]}, config=config)
```
