Flush output for real-time display:

```python
# Problem: Output not appearing in real-time
for chunk in model.stream("Long response"):
    print(chunk.content)  # May be buffered

# Solution: Use flush=True
for chunk in model.stream("Long response"):
    print(chunk.content, end="", flush=True)  # Real-time display
```
