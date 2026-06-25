Pass multiple stream modes as a list, not a string.
```python
# WRONG
graph.stream({}, stream_mode="updates, messages")

# CORRECT
graph.stream({}, stream_mode=["updates", "messages"])
```
