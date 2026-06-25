Use async libraries in async tools:

```python
import requests
import aiohttp

# BAD: Using sync in async context
@tool
async def bad_fetch(url: str) -> str:
    """Fetch URL."""
    response = requests.get(url)  # Blocking!
    return response.text

# GOOD: Use async libraries
@tool
async def good_fetch(url: str) -> str:
    """Fetch URL content."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```
