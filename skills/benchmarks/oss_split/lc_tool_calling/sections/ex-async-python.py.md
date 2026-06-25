Async tool execution with ainvoke.

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import asyncio

@tool
async def async_search(query: str) -> str:
    """Async search tool."""
    # Simulate async API call
    await asyncio.sleep(1)
    return f"Results for: {query}"

async def main():
    model = ChatOpenAI(model="gpt-4.1")
    model_with_tools = model.bind_tools([async_search])

    # Use ainvoke for async
    response = await model_with_tools.ainvoke("Search for Python")

    # Execute async tools
    tool_results = []
    for tool_call in response.tool_calls:
        result = await async_search.ainvoke(tool_call)
        tool_results.append(result)

    return tool_results

asyncio.run(main())
```
