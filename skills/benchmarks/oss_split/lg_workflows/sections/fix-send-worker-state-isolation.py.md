Workers receive isolated state:

```python
# WRONG - Workers share state, causing conflicts
class State(TypedDict):
    shared_counter: int  # All workers modify same counter!

# CORRECT - Each worker gets isolated input
def worker(state: dict) -> dict:
    # state is isolated to this worker
    return {"results": [process(state["task"])]}
```
