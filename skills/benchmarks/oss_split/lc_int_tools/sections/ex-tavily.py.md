Initialize Tavily search and use with agent.

```python
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# Initialize Tavily (requires API key)
search_tool = TavilySearchResults(
    max_results=3,
    api_key=os.getenv("TAVILY_API_KEY"),
)

# Use directly
results = search_tool.invoke("Latest AI news")
print(results)

# Use with agent
from langchain.agents import create_agent

agent = create_agent(model="gpt-4.1", tools=[search_tool])

response = agent.invoke({
    "messages": [{"role": "user", "content": "What's new in AI today?"}]
})
```
