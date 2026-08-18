Todo list state requires a thread_id for persistence across invocations.
```python
# WRONG: Fresh state each time without thread_id
agent.invoke({"messages": [...]})

# CORRECT: Use thread_id
config = {"configurable": {"thread_id": "user-session"}}
agent.invoke({"messages": [...]}, config=config)  # Todos preserved
```
