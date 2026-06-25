Iterate over stream correctly:

```python
# Problem: Not iterating stream
stream = model.stream("Hello")
print(stream)  # Generator object, not chunks

# Solution: Use for loop
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)
```
