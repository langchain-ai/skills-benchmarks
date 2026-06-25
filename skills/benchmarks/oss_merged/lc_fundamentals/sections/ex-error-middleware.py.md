Catch and handle tool errors gracefully with custom middleware.
```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
async def error_handler(tool_call, handler):
    try:
        return await handler(tool_call)
    except Exception as error:
        return {
            **tool_call,
            "content": f"Tool error: {str(error)}. Please try a different approach.",
        }

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[risky_tool],
    middleware=[error_handler],
)
```
