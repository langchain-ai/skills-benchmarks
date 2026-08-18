ToolMessage tool_call_id must match the original request.
```python
# WRONG
tool_message = ToolMessage(content="Sunny", tool_call_id="wrong_id", name="get_weather")

# CORRECT: Use ID from tool call (or let tool.invoke handle it)
tool_message = ToolMessage(content="Sunny", tool_call_id=response.tool_calls[0]["id"], name="get_weather")
tool_message = get_weather.invoke(response.tool_calls[0])  # Automatic
```
