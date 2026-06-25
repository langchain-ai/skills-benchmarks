Always pass tool results back to model.

```python
# Problem: Not passing tool results back to model
response1 = model_with_tools.invoke(messages)
tool_result = tool.invoke(response1.tool_calls[0])
# Missing: passing result back to model!

# Solution: Always pass results back
messages.append(response1)  # AI message with tool calls
messages.append(tool_result)  # Tool result
response2 = model_with_tools.invoke(messages)
```
