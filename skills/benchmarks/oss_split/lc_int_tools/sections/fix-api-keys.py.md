Provide API key via environment variable.

```python
# Missing API key
tool = TavilySearchResults()
tool.invoke("query")  # Error!

# Provide API key
import os
tool = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
```
