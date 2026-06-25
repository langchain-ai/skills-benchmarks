Iterate over stream or use invoke.

```python
# Wrong: Treating stream like regular response
response = model.stream("Hello")
print(response.content)  # AttributeError!

# Correct: Iterate over stream
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)

# OR use invoke for complete response
response = model.invoke("Hello")
print(response.content)
```
