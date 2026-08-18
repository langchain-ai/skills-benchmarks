Add checkpointer for short-term memory:

```python
# WRONG - No checkpointer, no memory
graph = builder.compile()  # Messages lost!

# CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
