Use array for multiple modes:

```python
# WRONG - Single string
graph.stream({}, stream_mode="updates, messages")

# CORRECT - List
graph.stream({}, stream_mode=["updates", "messages"])
```
