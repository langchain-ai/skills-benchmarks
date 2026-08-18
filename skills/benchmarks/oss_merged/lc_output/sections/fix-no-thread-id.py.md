Always provide thread_id when using HITL to track conversation state.
```python
# WRONG
agent.invoke(input)  # No config!

# CORRECT
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
