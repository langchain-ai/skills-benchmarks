Basic agent with search and weather tools:

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(model="gpt-4.1", tools=[search, get_weather])

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]
})
print(result["messages"][-1].content)
```
