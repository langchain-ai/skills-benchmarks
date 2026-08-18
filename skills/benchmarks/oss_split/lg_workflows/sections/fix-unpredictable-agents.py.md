Add iteration limits as guardrails:

```python
# RISKY - Pure agent, no guardrails
# Agent might loop forever or make bad choices

# BETTER - Hybrid with constraints
def should_continue(state):
    # Add max iterations check
    if state["iterations"] > 10:
        return END
    if state["messages"][-1].tool_calls:
        return "tools"
    return END
```
