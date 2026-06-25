Handle API errors gracefully in tools.

```python
from langchain_core.tools import tool
import requests

@tool
def api_call(endpoint: str) -> str:
    """Call external API.

    Args:
        endpoint: API endpoint to call
    """
    try:
        response = requests.get(f"https://api.example.com/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"API error: {str(e)}"

# Error handling is critical for robust tools
```
