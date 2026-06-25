Access response content correctly:

```python
# Problem: Wrong property access
response = model.invoke("Hello")
print(response)  # AIMessage object, not string

# Solution: Access .content property
print(response.content)  # "Hello! How can I help you?"

# Or convert to string
print(str(response))
```
