Bind all tools at once, not sequentially.

```python
# Problem: Binding tools overwrites previous binding
model = ChatOpenAI(model="gpt-4.1")
with_tool1 = model.bind_tools([tool1])
with_tool2 = with_tool1.bind_tools([tool2])  # Only has tool2!

# Solution: Bind all tools at once
with_both_tools = model.bind_tools([tool1, tool2])
```
