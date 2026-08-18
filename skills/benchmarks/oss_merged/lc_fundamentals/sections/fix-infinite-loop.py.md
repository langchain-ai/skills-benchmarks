Set recursion_limit in the invoke config to prevent runaway agent loops.
```python
# WRONG: No iteration limit - could loop forever
result = agent.invoke({"messages": [("user", "Do research")]})

# CORRECT: Set recursion_limit in config
result = agent.invoke(
    {"messages": [("user", "Do research")]},
    config={"recursion_limit": 10},  # Stop after 10 steps
)
```
