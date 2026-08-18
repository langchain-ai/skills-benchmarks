Enable persistence for interrupts:

```python
# WRONG - No checkpointer
graph = builder.compile()  # No persistence!
graph.invoke(...)  # Interrupt won't work

# CORRECT
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```
