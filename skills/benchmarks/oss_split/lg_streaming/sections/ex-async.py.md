Async streaming with astream:

```python
async for chunk in graph.astream(
    {"count": 0},
    stream_mode="values"
):
    print(chunk)
```
