Unpack messages mode tuple correctly:

```python
# Problem: Not unpacking messages mode
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    print(chunk.content)  # AttributeError!

# Solution: Messages mode returns (token, metadata) tuple
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)  # Correct!
```
