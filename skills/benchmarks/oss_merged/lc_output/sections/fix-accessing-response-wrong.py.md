Access structured output using the correct key.
```python
# WRONG
print(result["response"])  # KeyError!

# CORRECT
print(result["structured_response"])
```
