Tool return values must be JSON-serializable strings.
```python
# WRONG: datetime not JSON-serializable
@tool
def bad_get_time() -> datetime:
    return datetime.now()

# CORRECT
@tool
def good_get_time() -> str:
    return datetime.now().isoformat()
```
