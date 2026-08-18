Create a basic agent with a search tool and invoke it with a user message.
```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web."""
    return f"Results for: {query}"

agent = create_agent(
    model="gpt-4.1",
    tools=[search],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Search for AI news"}]
})
print(result["messages"][-1].content)
```
