Return correct type for reducer:

```python
# WRONG - Reducer expects list, but receives string
class State(TypedDict):
    items: Annotated[list, operator.add]

def bad_update(state: State) -> dict:
    return {"items": "not a list"}  # Type error!

# CORRECT
def good_update(state: State) -> dict:
    return {"items": ["item"]}
```
