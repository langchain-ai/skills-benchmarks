Async tool with aiohttp:

```python
from langchain.tools import tool
import aiohttp

@tool
async def fetch_weather(location: str) -> str:
    """Get current weather conditions for a location.

    Args:
        location: City name or ZIP code
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.weather.com/v1/location/{location}") as response:
            data = await response.json()
            return f"Temperature: {data['temp']}°F, Conditions: {data['conditions']}"
```
