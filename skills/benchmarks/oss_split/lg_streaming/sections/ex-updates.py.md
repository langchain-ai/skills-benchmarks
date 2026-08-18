Incremental state deltas:

```python
# Stream only the changes
for chunk in graph.stream(
    {"count": 0},
    stream_mode="updates"
):
    print(chunk)  # {"process": {"count": 1}}
```
