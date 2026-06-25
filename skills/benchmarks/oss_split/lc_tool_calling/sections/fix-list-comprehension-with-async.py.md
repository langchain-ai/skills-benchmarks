Use asyncio.gather for async list operations.

```python
# Problem: List comprehension with async
tool_results = [
    await tool.ainvoke(tc) for tc in response.tool_calls
]  # SyntaxError!

# Solution: Use asyncio.gather
tool_results = await asyncio.gather(
    *[tool.ainvoke(tc) for tc in response.tool_calls]
)

# Or traditional loop
tool_results = []
for tool_call in response.tool_calls:
    result = await tool.ainvoke(tool_call)
    tool_results.append(result)
```
