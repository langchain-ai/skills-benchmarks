Use string values for tool_choice.

```python
# Problem: Wrong type for tool_choice
model.bind_tools([tool], tool_choice=True)  # Wrong!

# Solution: Use string values
model.bind_tools([tool], tool_choice="any")  # Force any tool
model.bind_tools([tool], tool_choice="tool_name")  # Force specific
model.bind_tools([tool])  # tool_choice="auto" (default)
```
