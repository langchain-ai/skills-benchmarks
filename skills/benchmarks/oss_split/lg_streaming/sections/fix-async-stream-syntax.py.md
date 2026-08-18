Use async for with astream:

```python
# WRONG
for chunk in graph.astream({}):  # SyntaxError!
    print(chunk)

# CORRECT
async for chunk in graph.astream({}):
    print(chunk)
```
