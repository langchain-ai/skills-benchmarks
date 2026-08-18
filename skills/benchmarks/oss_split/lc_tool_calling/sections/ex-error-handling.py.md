Handle tool errors gracefully.

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import ToolMessage

@tool
def risky_tool(data: str = None) -> str:
    """A tool that might fail."""
    if not data:
        raise ValueError("Missing data")
    return "Success"

model = ChatOpenAI(model="gpt-4.1")
model_with_tools = model.bind_tools([risky_tool])

response = model_with_tools.invoke("Process this")

# Execute tools with error handling
tool_results = []
for tool_call in response.tool_calls:
    try:
        result = risky_tool.invoke(tool_call)
        tool_results.append(result)
    except Exception as error:
        # Return error as tool message
        tool_results.append(
            ToolMessage(
                content=f"Error: {str(error)}",
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        )
```
