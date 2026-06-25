Vague vs clear tool descriptions:

```python
# Bad: Vague tool description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""  # Too vague!
    return "result"

# Good: Clear, specific descriptions
@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data that wasn't in your training.

    Args:
        query: The search query (2-10 words)
    """
    return "result"
```
