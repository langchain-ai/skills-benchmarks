Add store for cross-thread memory:

```python
# WRONG - Trying to share data without store
# Can't access data from other threads with checkpointer alone!

# CORRECT - Use store
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```
