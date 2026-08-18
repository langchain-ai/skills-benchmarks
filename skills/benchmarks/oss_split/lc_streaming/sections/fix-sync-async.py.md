Use astream in async functions:

```python
# Problem: Using sync stream in async context
async def process():
    for mode, chunk in agent.stream(input):  # Blocks async loop!
        print(chunk)

# Solution: Use astream for async
async def process():
    async for mode, chunk in agent.astream(input):
        print(chunk)
```
