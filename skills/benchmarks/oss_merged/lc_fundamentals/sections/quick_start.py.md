Create and invoke a basic agent with tools using create_agent.
```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web.

    Args:
        query: The search query
    """
    return f"Results for: {query}"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[search],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({"messages": [("user", "Search for LangChain docs")]})
```
