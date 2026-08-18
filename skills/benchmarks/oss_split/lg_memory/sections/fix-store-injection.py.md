Inject store via parameter:

```python
# WRONG - Store not available
def my_node(state):
    store.put(...)  # NameError or wrong store!

# CORRECT - Inject via parameter
def my_node(state, *, store: BaseStore):
    store.put(...)  # Correct store instance
```
