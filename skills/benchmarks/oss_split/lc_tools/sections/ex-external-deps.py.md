Tool calling external API:

```python
from langchain.tools import tool
import requests
import os

@tool
def search_github(query: str, language: str = None) -> str:
    """Search GitHub repositories.

    Args:
        query: Search query
        language: Programming language filter (optional)
    """
    params = {"q": f"{query} language:{language}" if language else query, "sort": "stars"}
    headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}

    response = requests.get(
        "https://api.github.com/search/repositories",
        params=params,
        headers=headers,
    )

    repos = response.json()["items"][:5]
    return "\n".join([f"{r['full_name']} (stars: {r['stargazers_count']})" for r in repos])
```
