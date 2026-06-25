BAD vs GOOD descriptions:

```python
# BAD: Vague description
@tool
def bad_tool(data: str) -> str:
    """Does something with data."""  # Too vague!
    return "result"

# GOOD: Specific, actionable description
@tool
def search_customers(query: str) -> str:
    """Search customer database by name, email, or ID.

    Returns customer records with contact information.
    Use this when user asks about customer data.

    Args:
        query: Customer name, email, or ID to search for
    """
    return search_database(query)
```
