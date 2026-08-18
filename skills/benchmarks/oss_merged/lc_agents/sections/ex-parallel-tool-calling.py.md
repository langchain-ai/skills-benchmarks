Models may return multiple tool_calls at once - iterate over all of them.
```python
response = model_with_tools.invoke("Get weather for NYC and news about AI")

# Model may call both tools in parallel
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'NYC'}, 'id': 'call_1'},
#   {'name': 'get_news', 'args': {'topic': 'AI'}, 'id': 'call_2'}
# ]

# Execute ALL tool calls, not just the first one
for tool_call in response.tool_calls:
    result = tools_by_name[tool_call["name"]].invoke(tool_call)
```
