Force the model to use a specific tool or require at least one tool call.
```python
# Force model to use this specific tool
model_with_tools = model.bind_tools(
    [extract_info],
    tool_choice="extract_info"  # Must use this tool
)

# Or force any tool (model picks which)
model_with_tools = model.bind_tools(
    [tool1, tool2, tool3],
    tool_choice="any"
)
```
