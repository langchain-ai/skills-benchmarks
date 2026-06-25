Define and use async tools:

```python
from langchain.tools import tool

# Async tool properly defined
@tool
async def async_search(query: str) -> str:
    """Async search tool."""
    # Use await for async operations
    result = await some_async_api_call(query)
    return result

# Agent handles both sync and async tools
agent = create_agent(
    model="gpt-4.1",
    tools=[sync_tool, async_search],
)

# Use ainvoke for async execution
result = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Search something"}]
})
```
