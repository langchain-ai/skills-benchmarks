Limit iterations to prevent runaway agents:

```python
result = agent.invoke(
    {"messages": [("user", "Do research")]},
    config={"recursion_limit": 10},
)
```
