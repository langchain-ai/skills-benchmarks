Add max iterations check to prevent infinite loops.
```python
# RISKY: Might loop forever
def should_continue(state):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

# BETTER
def should_continue(state):
    if state["iterations"] > 10:
        return END
    if state["messages"][-1].tool_calls:
        return "tools"
    return END
```
