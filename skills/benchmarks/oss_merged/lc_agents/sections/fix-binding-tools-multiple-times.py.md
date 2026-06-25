Bind all tools at once - chaining bind_tools overwrites previous.
```python
# WRONG: Only has tool2
with_tool1 = model.bind_tools([tool1])
with_tool2 = with_tool1.bind_tools([tool2])

# CORRECT
with_both_tools = model.bind_tools([tool1, tool2])
```
