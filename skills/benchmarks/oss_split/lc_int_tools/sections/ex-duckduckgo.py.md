Search web without API key using DuckDuckGo.

```python
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

results = search_tool.invoke("LangChain framework")
print(results)

# With results object for more details
from langchain_community.tools import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(max_results=5)
results = search_tool.invoke("Python programming")
```
