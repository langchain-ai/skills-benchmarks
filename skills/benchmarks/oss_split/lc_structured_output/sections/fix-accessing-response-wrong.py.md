Access structured_response, not response.

```python
# Problem: Accessing wrong key
result = agent.invoke(input)
print(result["response"])  # KeyError!

# Solution: Use structured_response
print(result["structured_response"])
```
