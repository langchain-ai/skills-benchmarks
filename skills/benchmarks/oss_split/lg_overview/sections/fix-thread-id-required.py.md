Provide thread_id for persistence:

```python
# WRONG - No thread_id with checkpointer
agent.invoke({"messages": [...]})  # State not persisted!

# CORRECT - Always provide thread_id
agent.invoke(
    {"messages": [...]},
    {"configurable": {"thread_id": "user-123"}}
)
```
