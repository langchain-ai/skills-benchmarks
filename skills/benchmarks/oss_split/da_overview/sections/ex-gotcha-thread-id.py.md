Use thread_id for conversation continuity:

```python
# Each invocation is isolated without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]})
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]})

# Use consistent thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]}, config=config)
```
