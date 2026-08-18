Add type hints for proper schema generation.

```python
# Missing type hints
@tool
def my_tool(x):  # No type hints!
    return x

# Include type hints
@tool
def my_tool(x: str) -> str:
    """Process input.

    Args:
        x: Input string
    """
    return x.upper()
```
