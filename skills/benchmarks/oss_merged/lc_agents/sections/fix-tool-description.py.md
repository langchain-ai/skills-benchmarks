Use clear, specific descriptions so model knows when to use the tool.
```python
# WRONG: Vague
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""
    return "result"

# CORRECT
@tool
def web_search(query: str) -> str:
    """Search the web for current information.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```
