Always pass tool results back to the model.
```python
# WRONG: Missing results
response1 = model_with_tools.invoke(messages)
tool_result = tool.invoke(response1.tool_calls[0])

# CORRECT
messages.append(response1)
messages.append(tool_result)
response2 = model_with_tools.invoke(messages)
```
