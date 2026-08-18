Stream from nested graphs:

```python
# Include subgraph outputs
for chunk in graph.stream(
    {"data": "test"},
    stream_mode="updates",
    subgraphs=True  # Stream from nested graphs too
):
    print(chunk)
```
