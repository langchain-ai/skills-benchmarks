Check for `"__interrupt__"` in the result before assuming the agent completed.

Check for interrupt before processing result.

```python
# Problem: Not detecting interrupt
result = agent.invoke(input, config=config)
print(result["messages"])  # May not have completed!

# Solution: Check for __interrupt__
if "__interrupt__" in result:
    # Handle human decision
    pass
else:
    # Agent completed
    pass
```
