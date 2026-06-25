Create ToolMessage with correct tool_call_id.

```python
from langchain_core.messages import ToolMessage

# Tool messages link back to the tool call that requested them
tool_message = ToolMessage(
    content="Weather in Paris: Sunny, 72F",
    tool_call_id="call_abc123",  # Must match AIMessage tool_call id
    name="get_weather",  # Tool name
)

# Or created automatically by tool.invoke()
result = get_weather.invoke({
    "name": "get_weather",
    "args": {"location": "Paris"},
    "id": "call_abc123",
})
# result is a ToolMessage with proper structure
```
