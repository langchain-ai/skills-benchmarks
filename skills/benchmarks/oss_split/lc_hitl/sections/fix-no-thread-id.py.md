Always provide `thread_id` in config. Without it, the agent can't track state across invoke calls.

Include thread_id in config.

```python
# Problem: Missing thread_id
agent.invoke(input)  # No config!

# Solution: Always provide thread_id
agent.invoke(input, config={"configurable": {"thread_id": "user-123"}})
```
