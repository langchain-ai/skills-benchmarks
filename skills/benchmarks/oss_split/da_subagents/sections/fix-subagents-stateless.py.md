Each call creates fresh subagent:

```python
# Subagents don't remember previous calls
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='Find data')"}]})
agent.invoke({"messages": [{"role": "user", "content": "task(agent='research', instruction='What did you find?')"}]})
# Second call won't remember first call - fresh subagent each time

# Main agent maintains conversation memory, not subagents
```
