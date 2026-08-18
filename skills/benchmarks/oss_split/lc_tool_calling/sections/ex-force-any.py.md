Force model to use any tool.

```python
# Force model to use at least one tool (any of them)
model_with_tools = model.bind_tools(
    [tool1, tool2, tool3],
    tool_choice="any"
)

# Model must call at least one tool, can't respond with just text
response = model_with_tools.invoke("Process this data")
```
