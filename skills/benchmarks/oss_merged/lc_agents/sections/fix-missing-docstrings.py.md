Tools must have docstrings so model knows when to use them.
```python
# WRONG: No docstring
@tool
def bad_tool(input: str) -> str:
    return "result"

# CORRECT
@tool
def good_tool(input: str) -> str:
    """Process input data and return results.

    Args:
        input: The data to process
    """
    return "result"
```
