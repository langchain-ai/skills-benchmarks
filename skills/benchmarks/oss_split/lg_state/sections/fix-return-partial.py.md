Return partial updates only:

```python
# WRONG - Returning entire state object
def my_node(state: State) -> State:
    state["field"] = "updated"
    return state  # Don't do this!

# CORRECT - Return dict with updates
def my_node(state: State) -> dict:
    return {"field": "updated"}
```
