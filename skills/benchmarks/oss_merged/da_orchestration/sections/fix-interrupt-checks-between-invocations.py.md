Interrupts happen BETWEEN invoke() calls, not mid-execution.
```python
result = agent.invoke({...}, config=config)  # Step 1: invoke() -> interrupt triggers
state = agent.get_state(config)              # Step 2: Check state for interrupts
if state.next:                               # Has pending interrupts - handle them
    agent.update_state(config, {...})
    result = agent.invoke(None, config=config)  # Step 3: Resume
```
