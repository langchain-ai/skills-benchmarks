Set recursion_limit in invoke config to prevent agents from looping indefinitely.
```python
# PROBLEM: No stopping condition
result = agent.invoke({"messages": [("user", "Do research")]})

# SOLUTION: Set recursion_limit in config
result = agent.invoke(
    {"messages": [("user", "Do research")]},
    config={"recursion_limit": 10},
)
```
