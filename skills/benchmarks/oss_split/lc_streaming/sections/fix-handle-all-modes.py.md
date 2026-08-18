Check mode before accessing chunk data:

```python
# Problem: Not checking mode in multi-mode streaming
for mode, chunk in agent.stream(
    input,
    stream_mode=["updates", "messages"]
):
    print(chunk.content)  # Will fail for updates mode

# Solution: Check mode before accessing
for mode, chunk in agent.stream(
    input,
    stream_mode=["updates", "messages"]
):
    if mode == "messages":
        token, metadata = chunk
        print(token.content)
    elif mode == "updates":
        print(f"Step: {chunk}")
```
