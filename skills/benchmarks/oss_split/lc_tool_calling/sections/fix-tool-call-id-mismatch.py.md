Match tool_call_id from the response.

```python
# Problem: Wrong tool_call_id
response = model_with_tools.invoke("Get weather")
tool_message = ToolMessage(
    content="Sunny",
    tool_call_id="wrong_id",  # Doesn't match!
    name="get_weather",
)

# Solution: Use correct ID from tool call
tool_message = ToolMessage(
    content="Sunny",
    tool_call_id=response.tool_calls[0]["id"],  # Correct ID
    name="get_weather",
)

# OR use tool.invoke() which handles this automatically
tool_message = get_weather.invoke(response.tool_calls[0])
```
