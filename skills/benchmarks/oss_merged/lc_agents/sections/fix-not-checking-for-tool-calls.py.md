Check if tool_calls exist before executing.
```python
# WRONG: Assuming model always calls tools
tool.invoke(response.tool_calls[0])  # Error if no tool calls!

# CORRECT
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool.invoke(tool_call)
else:
    print(response.content)
```
