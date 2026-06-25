Handle missing values safely:

```python
# RISKY - No default, may cause errors
class State(TypedDict):
    count: int  # What if not initialized?

def increment(state: State) -> dict:
    return {"count": state["count"] + 1}  # KeyError!

# BETTER - Use .get() with default
def increment(state: State) -> dict:
    return {"count": state.get("count", 0) + 1}
```
