Clear descriptions help the agent know when to use each tool.
```python
# WRONG: Vague or missing description
@tool
def bad_tool(input: str) -> str:
    """Does stuff."""
    return "result"

# CORRECT: Clear, specific description with Args
@tool
def search(query: str) -> str:
    """Search the web for current information about a topic.

    Use this when you need recent data or facts.

    Args:
        query: The search query (2-10 words recommended)
    """
    return web_search(query)
```
