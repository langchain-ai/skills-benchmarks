Always use type hints:

```python
# BAD: No type hints
@tool
def bad_tool(query, limit):  # No types!
    """Search database."""
    return "result"

# GOOD: Always use type hints
@tool
def good_tool(query: str, limit: int = 10) -> str:
    """Search database.

    Args:
        query: Search terms or keywords
        limit: Maximum results to return (1-100)
    """
    return "result"
```
