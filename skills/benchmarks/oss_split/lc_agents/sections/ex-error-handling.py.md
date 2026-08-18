Custom error handling middleware:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call

# Custom error handling middleware
@wrap_tool_call
async def error_handler(tool_call, handler):
    try:
        return await handler(tool_call)
    except Exception as error:
        return {
            **tool_call,
            "content": f"Tool error: {str(error)}",
        }

agent = create_agent(
    model="gpt-4.1",
    tools=[risky_tool],
    middleware=[error_handler],
)
```
