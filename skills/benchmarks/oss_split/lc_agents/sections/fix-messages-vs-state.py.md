Access result messages correctly:

```python
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
print(result["messages"])  # List of all messages - correct
# print(result.content)    # KeyError! - wrong
```
