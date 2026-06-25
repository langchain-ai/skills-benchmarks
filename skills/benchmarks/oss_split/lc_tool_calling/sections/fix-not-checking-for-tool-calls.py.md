Check if tool_calls exist before using.

```python
# Problem: Assuming model always calls tools
response = model_with_tools.invoke("Hello")
tool.invoke(response.tool_calls[0])  # Error if no tool calls!

# Solution: Check if tool calls exist
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool.invoke(tool_call)
else:
    # Model responded without calling tools
    print(response.content)
```
