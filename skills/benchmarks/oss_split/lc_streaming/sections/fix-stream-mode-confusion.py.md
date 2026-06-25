Use messages mode for token streaming:

```python
# Problem: Using wrong mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["updates"]):
    print(chunk.content)  # AttributeError!

# Solution: Use "messages" mode for tokens
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)
```
