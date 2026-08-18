Interrupts occur between invoke calls:

```python
# Interrupts don't happen mid-invoke()
# They happen between invoke() calls

# Step 1: invoke() -> interrupt occurs
result = agent.invoke({...}, config=config)

# Step 2: Check state for interrupts
state = agent.get_state(config)
if state.next:  # Has interrupts
    # Handle interrupts

# Step 3: Resume with decision
agent.update_state(config, {...})
result = agent.invoke(None, config=config)
```
