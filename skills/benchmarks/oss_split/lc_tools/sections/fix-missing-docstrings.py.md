Always provide docstrings:

```python
# BAD: No docstring
@tool
def bad_tool(input: str) -> str:
    return "result"  # No description!

# GOOD: Always provide docstring
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Use this tool when you need to transform user input.

    Args:
        input: The data to process
    """
    return "result"
```
