Reducer expects specific type - return value must match.
```python
# WRONG: Reducer expects list
return {"items": "not a list"}  # Type error!

# CORRECT
return {"items": ["item"]}
```
