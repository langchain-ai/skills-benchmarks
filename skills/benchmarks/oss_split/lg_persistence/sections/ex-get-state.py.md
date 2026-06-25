Get current state and history:

```python
# Get current state
config = {"configurable": {"thread_id": "conversation-1"}}
current_state = graph.get_state(config)
print(current_state.values)  # Current state
print(current_state.next)    # Next nodes to execute

# Get state history
for state in graph.get_state_history(config):
    print(f"Step: {state.values}")
```
